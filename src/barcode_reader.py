import os
from PIL import Image
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
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {image_path}")
    except Exception as e:
        raise ValueError(f"An error occurred while opening the image: {e}")

    barcodes = decode(image)
    if not barcodes:
        raise ValueError("No barcodes found in the image.")

    access_key = barcodes[0].data.decode('utf-8')
    if not access_key.isdigit() or len(access_key) != 44:
        raise ValueError("Invalid barcode data.")
    
    return access_key