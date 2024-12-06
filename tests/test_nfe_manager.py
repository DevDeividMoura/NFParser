import pytest
from pathlib import Path
from unittest.mock import patch
from src.nfe_manager import fetch_nfe_xml, extract_nfe_data

# Test resource directory
RESOURCE_TEST_DIR = Path(__file__).resolve().parent / "resources"

# Constants for the test
ACCESS_KEY = "9" * 44
BASE_URL = "https://exemple.domain.com"

# Read the test XML file
NFE_XML = (RESOURCE_TEST_DIR / "nfe.xml").read_text()

def mocked_requests_post(url, data=None, **kwargs):
    """
    Mock function for httpx.post to simulate API behavior.

    Args:
        url (str): The request URL.
        data (dict): The request payload.
        kwargs: Additional arguments.

    Returns:
        MockResponse: A simulated response object.
    """
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP Error: {self.status_code}")

    if url == f"{BASE_URL}/api/v1/get/nfe/xml/{ACCESS_KEY}":
        return MockResponse(NFE_XML.encode(), 200)
    elif url == f"{BASE_URL}/api/v1/get/nfe/data/MEUDANFE/{ACCESS_KEY}":
        return MockResponse(None, 200)  # Simulate successful caching
    else:
        return MockResponse(None, 404)

@patch("httpx.post", side_effect=mocked_requests_post)
def test_fetch_nfe_xml_valid_access_key(mock_post):
    """
    Test fetching the XML with a valid access key.

    Verifies:
    - The returned content matches the expected XML.
    - The mocked httpx.post is called exactly once.
    - The correct URL is passed to the post request.
    """
    # Act
    result = fetch_nfe_xml(ACCESS_KEY, base_url=BASE_URL)

    # Assert
    assert result == NFE_XML.encode(), "The XML content was not downloaded correctly."
    assert mock_post.call_count == 1, "httpx.post was not called exactly once."

def test_extract_nfe_data():
    """
    Test extracting data from the NFe XML content.

    Verifies:
    - The extracted data matches the expected values.
    """

    # Arrange
    expected_data = {
        "date": "30/11/2024",
        "amount": "425,01",
        "plate": "ABC-1234",
        "km": "62876"
    }

    # Act
    data = extract_nfe_data(NFE_XML)

    # Assert
    assert data == expected_data, "The extracted data does not match the expected data."

def test_extract_nfe_data_missing_plate_km():
    
    # Arrange
    nfe_xml = NFE_XML.replace("ABC-1234", "")
    nfe_xml = nfe_xml.replace("62876", "")

    expected_data = {
        "date": "30/11/2024",
        "amount": "425,01",
        "plate": "N/A",
        "km": "N/A"
    }

    # Act
    data = extract_nfe_data(nfe_xml)

    # Assert
    assert data == expected_data, "The extracted data does not match the expected data."

def test_extract_nfe_data_missing_datas():
        
    # Arrange
    nfe_xml = NFE_XML.replace("2024-11-30T13:23:32-03:00", "")
    nfe_xml = nfe_xml.replace("Placa: ABC-1234 - KM: 62.876", "")
    nfe_xml = nfe_xml.replace("425.01", "")

    # Act
    data = extract_nfe_data(nfe_xml)

    # Assert
    assert data == None, "The extracted data does not match the expected data."

def test_extract_nfe_data_invalid_xml():
        
    # Arrange
    nfe_xml = NFE_XML.replace("<NFe>", "<nfe")

    # Act
    with pytest.raises(ValueError, match="Invalid XML content"):
        extract_nfe_data(nfe_xml)