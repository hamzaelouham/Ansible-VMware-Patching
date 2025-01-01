import aiohttp
import asyncio


async def session(hostname=None,username=None,password=None,validate_certs=False):
                API_ENDPOINT = "/rest/com/vmware/cis/session"
                auth = aiohttp.BasicAuth(username, password)
                connector = aiohttp.TCPConnector(ssl=validate_certs)

                async with aiohttp.ClientSession(connector=connector) as session:
                    try:
                        async with session.post(f"https://{hostname}{API_ENDPOINT}", auth=auth) as response:

                            if response.status == 200:
                                data = await response.json()
                                return data["value"]
                            else:
                                print(f"Authentication failed. Status: {response.status}")
                                print(f"Response: {await response.text()}")
                                return None
                    except aiohttp.ClientError as e:
                        print(f"Error connecting to vCenter: {e}")
                        return None