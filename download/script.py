from msal import ConfidentialClientApplication
import requests
import shutil
import os

# ==============================
# Configuration
# ==============================
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

SITE_URL = "atos365.sharepoint.com:/sites/100004478"  # Update with your site URL
DOCUMENT_LIBRARY_NAME = "Documents"  # Update if different
DOWNLOAD_PATH = "/home/atosadm/gppDownloads"
FOLDER_PATH = "Atos_Global_Images/Linux/Linux_OVF_Template"  # Folder in SharePoint


# ==============================
# Authentication
# ==============================
def get_access_token():
    """Authenticate and get an access token for Microsoft Graph API."""
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY,
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Failed to acquire access token:", result.get("error_description"))


# ==============================
# SharePoint Helper Functions
# ==============================
def get_site_id(access_token):
    """Retrieve the Site ID for the given SharePoint site."""
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://graph.microsoft.com/v1.0/sites/{SITE_URL}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        raise Exception(f"Error getting site ID: {response.status_code}, {response.text}")


def get_drive_id(access_token, site_id):
    """Retrieve the Drive ID for the document library."""
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        drives = response.json().get("value", [])
        for drive in drives:
            if drive["name"] == DOCUMENT_LIBRARY_NAME:
                return drive["id"]
        raise Exception(f"Drive '{DOCUMENT_LIBRARY_NAME}' not found.")
    else:
        raise Exception(f"Error getting drive ID: {response.status_code}, {response.text}")


def list_folder_contents(access_token, site_id, drive_id, folder_path):
    """Retrieve all items (folders and files) in a SharePoint folder, handling pagination."""
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{folder_path.strip('/')}:/children"
    items = []

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            items.extend(data.get("value", []))
            url = data.get("@odata.nextLink")  # Handle pagination
        else:
            raise Exception(f"Error listing folder contents: {response.status_code}, {response.text}")

    return items


# ==============================
# Download Logic (ZIP only)
# ==============================
def download_folder(access_token, site_id, drive_id, folder_path, local_path, is_root=True):
    """
    Recursively download only .zip files from a SharePoint folder and its subfolders.
    """
    items = list_folder_contents(access_token, site_id, drive_id, folder_path)

    for item in items:
        item_name = item["name"]

        # ✅ If it's a folder, go inside (recursive)
        if "folder" in item:
            print(f"Entering folder: {item_name}")
            download_folder(access_token, site_id, drive_id, f"{folder_path}/{item_name}", local_path, is_root=False)

        # ✅ If it's a file and ends with .zip, download it
        elif "file" in item and item_name.lower().endswith(".zip"):
            os.makedirs(local_path, exist_ok=True)
            file_path = os.path.join(local_path, item_name)
            file_url = item["@microsoft.graph.downloadUrl"]

            print(f"Downloading ZIP file: {item_name}")
            with requests.get(file_url, stream=True) as response:
                response.raise_for_status()
                with open(file_path, "wb") as file:
                    shutil.copyfileobj(response.raw, file)

        # ✅ Skip all other files
        else:
            print(f"Skipping non-ZIP file: {item_name}")

    if is_root:
        print(f"✅ Download completed for: {folder_path}")


# ==============================
# Main Execution
# ==============================
if __name__ == "__main__":
    try:
        print("Authenticating to Microsoft Graph API...")
        token = get_access_token()
        print("Access token acquired successfully!")

        print("Fetching SharePoint Site ID...")
        site_id = get_site_id(token)

        print(f"Fetching Drive ID for '{DOCUMENT_LIBRARY_NAME}'...")
        drive_id = get_drive_id(token, site_id)

        print(f"Starting ZIP download from '{FOLDER_PATH}' into '{DOWNLOAD_PATH}'...")
        download_folder(token, site_id, drive_id, FOLDER_PATH, DOWNLOAD_PATH)

    except Exception as e:
        print(f"❌ Error: {e}")
