import requests
from requests.exceptions import RequestException

def fetch_nfe_xml(access_key, base_url="https://ws.meudanfe.com/api/v1/get/nfe/xml/"):
    """
    Fetches the XML of a NFe using the provided access key.

    Args:
        access_key (str): The access key for the NFe.
        base_url (str): The base URL of the API (default is Meudanfe API URL).

    Returns:
        bytes: The content of the XML if successful.
        None: If an error occurs.
    """
    url = f"{base_url}{access_key}"
    
    try:
        response = requests.post(url, data="empty")
        response.raise_for_status()
        return response.content

    except RequestException as err:
        # Log or handle the error if necessary
        print(f"Error fetching NFe XML: {err}")
        return None
