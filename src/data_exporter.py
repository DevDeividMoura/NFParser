import openpyxl
from openpyxl.styles import Font

def save_to_excel(data, file_path):
    """
    Saves the given data to an Excel file.
    
    Args:
        data (list): List of dictionaries containing the data to be saved.
        file_path (str): Path to the output Excel file.
    """

    # Criar um novo workbook e selecionar a sheet ativa
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Definir os cabeçalhos
    headers = ["date", "station", "amount", "plate", "km"]
    sheet.append(headers)

    # Estilizar os cabeçalhos (opcional)
    for cell in sheet[1]:
        cell.font = Font(bold=True)

    # Preencher os dados
    station = "deluca"
    for row in data:
        sheet.append([
            row.get("date", ""),
            station,
            row.get("amount", ""),
            row.get("plate", ""),
            row.get("km", ""),
        ])

    # Salvar o arquivo Excel
    workbook.save(file_path)

import csv

def save_to_csv(data, file_path):
    """
    Saves the given data to a CSV file.
    
    Args:
        data (list): List of dictionaries containing the data to be saved.
        file_path (str): Path to the output CSV file.
    """
    # Definir os cabeçalhos
    headers = ["date", "station", "amount", "plate", "km"]
    station = "deluca"  # Valor fixo para a coluna 'station'
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # Escrever os cabeçalhos
        writer.writeheader()
        
        # Escrever os dados
        for row in data:
            writer.writerow({
                "date": row.get("date", ""),
                "station": station,
                "amount": row.get("amount", ""),
                "plate": row.get("plate", ""),
                "km": row.get("km", ""),
            })

