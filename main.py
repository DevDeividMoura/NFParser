# import os
import csv
# import time
# from pathlib import Path
# from src.barcode_reader import extract_access_key
from src.nfe_manager import fetch_nfe_xml, extract_nfe_data
from src.data_exporter import save_to_excel

with open('access_keys.txt', 'r') as file:
    access_keys = file.read().splitlines()

def process_images(image_folder: str, output_csv: str):
    # image_folder = Path(image_folder)
    results = []
    
    # if not image_folder.exists() or not image_folder.is_dir():
    #     raise FileNotFoundError(f"The folder {image_folder} does not exist or is not a directory.")
    
    # for image_file in image_folder.iterdir():
    #     if image_file.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.bmp'}:
    #         continue
        
    for access_key in access_keys:   
        try:
            # access_key = extract_access_key(str(image_file))
            print(f"Processing Access Key: {access_key}")
            xml_content = fetch_nfe_xml(access_key)
            #   print(f"XML Content: {xml_content}")
            nfe_data = extract_nfe_data(xml_content)
            #   print(f"Extracted Data: {nfe_data}")
            
            if nfe_data:
                results.append(nfe_data)
        except Exception as e:
            print(f"Error processing {access_key}: {e}")
    
    if results:
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['date', 'amount', 'plate', 'km'])
            writer.writeheader()
            writer.writerows(results)
        
        save_to_excel(results, output_csv.replace('.csv', '.xlsx'))
        print(f"Report saved to {output_csv} and {output_csv.replace('.csv', '.xlsx')}")
    else:
        print("No valid data extracted.")

if __name__ == "__main__":
    process_images("images", "report.csv")
