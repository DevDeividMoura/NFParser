# NFParser - Automation for Extracting and Processing NF-e Information

**NFParser** is an automation tool developed to simplify the process of extracting data from Brazilian electronic invoices (NF-e), including reading barcodes, downloading XML files, extracting important information and saving data in Excel spreadsheets. This project aims to automate and speed up the processing of electronic invoices in commercial operations.

## Features

- **Barcode Scanning**: Extracts the access key from barcode images of invoices.
- **XML Download**: Downloads the NFe XML file using the access key.
- **XML Parsing**: Extracts relevant data such as issue date, amount paid, license plate, and kilometers from the XML.
- **Excel Export**: Saves the extracted data into an Excel spreadsheet for easy analysis and reporting.
- **Logging**: Logs the application's activity for troubleshooting and monitoring.

## Prerequisites

Before you start, make sure you have the following installed on your system:

- Python 3.10+
- Poetry (Python's package manager)


