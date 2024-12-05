import httpx
from httpx import URL, HTTPStatusError

def enforce_trailing_slash(url: URL) -> URL:
    """
    Ensures the URL has a trailing slash.

    Args:
        url (URL): The URL to enforce the trailing slash.

    Returns:
        URL: The modified URL with a trailing slash.
    """
    if url.raw_path.endswith(b"/"):
        return url
    return url.copy_with(raw_path=url.raw_path + b"/")

def fetch_nfe_xml(access_key: str, base_url: str | URL = "https://ws.meudanfe.com") -> bytes:
    """
    Fetches the XML of a NFe using the provided access key.

    Args:
        access_key (str): The access key for the NFe.
        base_url (str | URL): The base URL of the API (default is Meudanfe API URL).

    Returns:
        bytes: The content of the XML if successful.

    Raises:
        HTTPStatusError: If an error occurs during any HTTP request.
        ValueError: If the access key is invalid.
    """
    if not (isinstance(access_key, str) and access_key.isdigit() and len(access_key) == 44):
        raise ValueError("Invalid access key. Must be a 44-digit numeric string.")

    base_url = enforce_trailing_slash(URL(base_url))

    # Build URLs for XML and data endpoints
    url_xml = base_url.join(f"/api/v1/get/nfe/xml/{access_key}")
    url_data = base_url.join(f"/api/v1/get/nfe/data/MEUDANFE/{access_key}")

    try:
        # Attempt to fetch XML
        response = httpx.post(url_xml, data="empty")
        response.raise_for_status()
        return response.content

    except HTTPStatusError as e:
        if e.response.status_code == 400:
            # XML not cached, fetch data to cache it
            response = httpx.post(url_data, data="empty")
            response.raise_for_status()

            # Retry fetching the XML
            response = httpx.post(url_xml, data="empty")
            response.raise_for_status()
            return response.content
        else:
            raise HTTPStatusError(
                f"Error fetching NFe XML: {e.response.status_code}",
                request=e.request,
                response=e.response,
            )