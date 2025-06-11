import re
import random
import httpx
from datetime import datetime
import xml.etree.ElementTree as ET
from httpx import URL, HTTPStatusError

from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent

# with open(BASE_DIR / "proxies.txt", "r") as file:
#     PROXIES = file.read().splitlines()

PROXIES = [
    "23.247.136.245:80",
    "57.129.49.182:3128",
    "188.32.100.60:8080",
    "8.221.139.222:8443",
    "52.16.232.164:3128",
    "8.211.194.85:312"
]

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
    Now supports proxy rotation to avoid request blocking.

    Args:
        access_key (str): The access key for the NFe.
        base_url (str | URL): The base URL of the API.

    Returns:
        bytes: The content of the XML if successful.

    Raises:
        HTTPStatusError: If an error occurs during any HTTP request.
        ValueError: If the access key is invalid.
    """
    if not (isinstance(access_key, str) and access_key.isdigit() and len(access_key) == 44):
        raise ValueError(
            "Invalid access key. Must be a 44-digit numeric string.")

    base_url = enforce_trailing_slash(URL(base_url))

    url_xml = base_url.join(f"/api/v1/get/nfe/xml/{access_key}")
    url_data = base_url.join(f"/api/v1/get/nfe/data/MEUDANFE/{access_key}")

    proxy = random.choice(PROXIES)  # Escolhe um proxy aleatoriamente

    proxy_mounts = {
        # "http://": httpx.HTTPTransport(proxy=f"http://{proxy}"),
        # "https://": httpx.HTTPTransport(proxy=f"http://{proxy}"),
    }
    # print(f"Using proxy: {proxy}")

    try:
        with httpx.Client() as client:
            response = client.post(url_xml, data="empty")
            response.raise_for_status()
            return response.content

    # except HTTPStatusError as e:
    #     if e.response.status_code == 500:
    #         with httpx.Client() as client:
    #             response = client.post(url_data, data="empty")
    #             response.raise_for_status()

    #             response = client.post(url_xml, data="empty")
    #             response.raise_for_status()
    #             return response.content
    except HTTPStatusError as e:
        if e.response.status_code in [400, 500]:
            with httpx.Client() as client:
                response = client.post(url_data, data="empty")
                response.raise_for_status()

                response = client.post(url_xml, data="empty")
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
    xml_content = xml_content if isinstance(
        xml_content, str) else xml_content.decode("utf-8")

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

    def extract_plate_km(info_cpl: str) -> tuple[str, str]:
        """
        Extracts a vehicle plate and kilometer/odometer reading from a string.

        This function attempts to find the plate and kilometer reading using two
        different patterns to accommodate variations in the input format. It first
        searches for a "Placa/KM" pattern and, if not found, searches for a
        "Placa/ODOMETRO" pattern.

        Args:
            info_cpl: The input string containing the information.

        Returns:
            A tuple containing the plate and the cleaned kilometer value as strings.
            Example: ("RKW5F47", "140819").
            If no match is found, it returns ("N/A", "N/A").
        """
        # Pattern 1: Searches for "Placa" and "KM"
        pattern_km = r"Placa:.*?([A-Z0-9\-]+).*?KM:.*?([\d\.,]+)"
        match_km = re.search(pattern_km, info_cpl, re.IGNORECASE)

        if match_km:
            plate = match_km.group(1).upper()
            km_raw = match_km.group(2)

            # Robustly clean the kilometer string from the "KM" pattern
            km_cleaned = km_raw.replace('.', '').replace(',', '.')
            return plate, km_cleaned

        # Pattern 2: Searches for "Placa" and "ODOMETRO"
        pattern_odometro = r"PLACA:.*?([A-Z0-9\-]+).*?ODOMETRO:.*?(\d+)"
        match_odometro = re.search(pattern_odometro, info_cpl, re.IGNORECASE)

        if match_odometro:
            plate = match_odometro.group(1).upper()
            # The odometer value is expected to be a clean integer string already
            km_value = match_odometro.group(2)
            return plate, km_value

        # If neither pattern matched, return default values
        return "N/A", "N/A"

    date = format_date(get_text_from_xpath(".//nfe:dhEmi"))
    amount = format_amount(get_text_from_xpath(
        './/nfe:pag/nfe:detPag/nfe:vPag'))
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
