import os
from PIL import Image, UnidentifiedImageError
from pyzbar.pyzbar import decode
from typing import Union

def extract_access_key(image_path: Union[str, bytes, os.PathLike]) -> str:
    """
    Extracts the access key from a barcode in the given image.

    Args:
        image_path (Union[str, bytes, os.PathLike]): The path to the image file.

    Returns:
        str: The extracted access key.

    Raises:
        FileNotFoundError: If the image file does not exist.
        ValueError: If no barcodes are found or if the barcode data is invalid.
    """
    # Ensure the file exists before processing
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    try:
        # Open the image file
        image = Image.open(image_path)
    except UnidentifiedImageError:
        raise ValueError("The provided file is not a valid image.")
    except Exception as e:
        raise ValueError(f"An error occurred while opening the image: {e}")

    # Decode barcodes in the image
    barcodes = decode(image)
    if not barcodes:
        raise ValueError("No barcodes found in the image.")

    # Extract and validate the first barcode
    access_key = barcodes[0].data.decode('utf-8')
    if not access_key.isdigit() or len(access_key) != 44:
        raise ValueError("Invalid barcode data. Expected a 44-digit numeric access key.")

    return access_key
