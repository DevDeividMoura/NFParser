import pytest
from pathlib import Path
from unittest.mock import patch
from src.nfe_manager import fetch_nfe_xml

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