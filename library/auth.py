import aiohttp
import asyncio

async def authenticate_vcenter(vcenter_hostname, username, password):
    """
    Authenticate to VMware vCenter and retrieve a session ID, ignoring SSL certificate validation.

    Args:
        vcenter_hostname (str): The hostname or IP address of the vCenter server.
        username (str): Username for vCenter authentication.
        password (str): Password for vCenter authentication.

    Returns:
        str: A session ID token for authenticated requests.
    """
    auth_url = f"https://{vcenter_hostname}/rest/com/vmware/cis/session"
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.post(auth_url, auth=aiohttp.BasicAuth(username, password)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("value")  # The session ID
                else:
                    print(f"Authentication failed with status {response.status}: {await response.text()}")
                    return None
        except aiohttp.ClientError as e:
            print(f"Error connecting to vCenter: {e}")
            return None


# Example usage
async def main():
    vcenter_hostname = "vcenter.example.com"
    username = "administrator@vsphere.local"
    password = "your_password"
    
    session_id = await authenticate_vcenter(vcenter_hostname, username, password)
    if session_id:
        print(f"Authentication successful! Session ID: {session_id}")
    else:
        print("Authentication failed.")

# Run the example
if __name__ == "__main__":
    asyncio.run(main())
