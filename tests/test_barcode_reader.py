import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.barcode_reader import extract_access_key

RESOURCE_TEST_DIR = Path(__file__).resolve().parent / "resources"

def test_extract_access_key_valid_image():
    # Arrange
    image_path = RESOURCE_TEST_DIR / "valid_barcode.png"
    expected_access_key = "42241182904210000179550040000056131301323325"

    # ACT
    result = extract_access_key(image_path)

    # Assert
    assert result == expected_access_key, "Access key was not extracted correctly"

def test_extract_access_key_file_not_found():
    image_path = "non_existent_image.png"

    with pytest.raises(FileNotFoundError):
        extract_access_key(image_path)

def test_extract_access_key_no_barcode():
    image_path = RESOURCE_TEST_DIR / "no_barcode.png"

    with pytest.raises(ValueError, match="No barcodes found in the image."):
        extract_access_key(image_path)

def test_extract_access_key_invalid_barcode():
    image_path = RESOURCE_TEST_DIR / "invalid_barcode.png"

    with pytest.raises(ValueError, match="Invalid barcode data."):
        extract_access_key(image_path)