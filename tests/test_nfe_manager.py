import pytest
from pathlib import Path
from unittest.mock import patch
from src.nfe_manager import fetch_nfe_xml

# Test resource directory
RESOURCE_TEST_DIR = Path(__file__).resolve().parent / "resources"

# Constants for the test
ACCESS_KEY = "9" * 44
TEST_URL = "https://exemple.domain.com/api/v1/get/nfe/xml/"

# Read the test XML file
NFE_XML = (RESOURCE_TEST_DIR / "nfe.xml").read_text()

def mocked_requests_post(url, data=None, **kwargs):
    """
    Mock function for requests.post to simulate API behavior.

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
            if self.status_code != 200:
                raise Exception(f"HTTP Error: {self.status_code}")

    # Return a valid response for the expected URL
    if url == f"{TEST_URL}{ACCESS_KEY}":
        return MockResponse(NFE_XML.encode(), 200)  # Return content as bytes

    # Return a 404 response for other URLs
    return MockResponse(None, 404)

@patch("requests.post", side_effect=mocked_requests_post)
def test_fetch_nfe_xml_valid_access_key(mock_post):
    """
    Test fetching the XML with a valid access key.

    Verifies:
    - The returned content matches the expected XML.
    - The mocked requests.post is called exactly once.
    - The correct URL is passed to the post request.
    """
    # Act
    result = fetch_nfe_xml(ACCESS_KEY, base_url=TEST_URL)

    # Assert
    assert result == NFE_XML.encode(), "The XML content was not downloaded correctly."
    assert mock_post.call_count == 1, "requests.post was not called exactly once."
    mock_post.assert_called_with(
        f"{TEST_URL}{ACCESS_KEY}",
        data="empty",  # The `data` parameter is empty in the original code
    )
