import pytest
from pathlib import Path
from src.barcode_reader import extract_access_key

# Directory containing test resources
RESOURCE_TEST_DIR = Path(__file__).resolve().parent / "resources"

def test_extract_access_key_valid_image():
    """
    Test extraction of access key from a valid barcode image.
    """
    # Arrange
    image_path = RESOURCE_TEST_DIR / "valid_barcode.png"
    expected_access_key = "9" * 44

    # Act
    result = extract_access_key(image_path)

    # Assert
    assert result == expected_access_key, "The extracted access key does not match the expected value."

def test_extract_access_key_file_not_found():
    """
    Test behavior when the image file does not exist.
    """
    # Arrange
    image_path = "non_existent_image.png"

    # Act & Assert
    with pytest.raises(FileNotFoundError, match=f"File not found: {image_path}"):
        extract_access_key(image_path)

def test_extract_access_key_no_barcode():
    """
    Test behavior when no barcodes are present in the image.
    """
    # Arrange
    image_path = RESOURCE_TEST_DIR / "no_barcode.png"

    # Act & Assert
    with pytest.raises(ValueError, match="No barcodes found in the image."):
        extract_access_key(image_path)

def test_extract_access_key_invalid_barcode():
    """
    Test behavior when the barcode data is invalid.
    """
    # Arrange
    image_path = RESOURCE_TEST_DIR / "invalid_barcode.png"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid barcode data. Expected a 44-digit numeric access key."):
        extract_access_key(image_path)
