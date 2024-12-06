import re
import httpx
from datetime import datetime
import xml.etree.ElementTree as ET
from httpx import URL, HTTPStatusError

NFE_NAMESPACE = {"nfe": "http://www.portalfiscal.inf.br/nfe"}

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
        
def extract_nfe_data(xml_content: str | bytes) -> dict:
    """
    Extracts relevant data from the XML content of a NFe.

    Args:
        xml_content (str | bytes): The content of the NFe XML.

    Returns:
        dict: A dictionary containing the extracted data.
    """
    xml_content = xml_content if isinstance(xml_content, str) else xml_content.decode("utf-8")
    
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise ValueError("Invalid XML content") from e

    ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}

    def get_text_from_xpath(xpath: str) -> str:
        element = root.find(xpath, ns)
        return element.text if element is not None else None

    def format_date(date_str: str) -> str:
        try:
            return datetime.fromisoformat(date_str[:-6]).strftime('%d/%m/%Y') if date_str else None
        except ValueError:
            return "Invalid date"

    def format_amount(amount_str: str) -> str:
        return amount_str.replace('.', ',') if amount_str else None

    def extract_plate_km(info_cpl: str) -> tuple:
        plate_km = re.findall(r'Placa: ([A-Z0-9\-]+).*KM: ([\d\.,]+)', info_cpl)
        if plate_km:
            plate, km = plate_km[0]
            km = km.replace('.', '')
            return plate, km
        return "N/A", "N/A"

    date = format_date(get_text_from_xpath(".//nfe:dhEmi"))
    amount = format_amount(get_text_from_xpath('.//nfe:pag/nfe:detPag/nfe:vPag'))
    info_cpl = get_text_from_xpath('.//nfe:infAdic/nfe:infCpl')
    plate, km = extract_plate_km(info_cpl) if info_cpl else ("N/A", "N/A")

    if all(value for value in (date, amount)):
        return {
            "date": date,
            "amount": amount,
            "plate": plate,
            "km": km
        }
    
    return None