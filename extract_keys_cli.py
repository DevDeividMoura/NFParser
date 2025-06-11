import re
import sys

def extract_access_keys_from_html(html_content):
    """
    Finds all 44-digit numeric sequences in a given HTML string.

    Args:
        html_content (str): A string containing the HTML source code.

    Returns:
        list: A list of strings, where each string is a 44-digit access key.
    """
    pattern = r'\b(\d{44})\b'
    access_keys = re.findall(pattern, html_content)
    return access_keys

def save_keys_to_file(keys, filename="chaves_de_acesso.txt"):
    """
    Saves a list of keys to a text file, with each key on a new line.

    Args:
        keys (list): A list of strings to be written to the file.
        filename (str): The name of the output file.
    """
    if not keys:
        print("info: 🤷 No keys were found to save.")
        return

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for key in keys:
                f.write(key + '\n')
        # A mensagem de sucesso agora reflete o número de chaves *únicas* salvas.
        print(f"feat: ✨ Successfully saved {len(keys)} unique keys to {filename}")
    except IOError as e:
        print(f"error: 🔥 Failed to write to file {filename}. Reason: {e}")

# --- Main execution block ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_keys_cli.py <path_to_html_file>")
        sys.exit(1)

    html_file_path = sys.argv[1]

    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_source = f.read()
    except FileNotFoundError:
        print(f"error: 🔥 File not found at '{html_file_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"error: 🔥 An unexpected error occurred while reading the file: {e}")
        sys.exit(1)

    # 1. Extract all occurrences, including duplicates
    all_found_keys = extract_access_keys_from_html(html_source)
    
    # 2. Remove duplicates while preserving order
    unique_keys = list(dict.fromkeys(all_found_keys)) # 👈 AQUI ESTÁ A MUDANÇA
    
    # 3. Report the result
    total_found = len(all_found_keys)
    total_unique = len(unique_keys)
    duplicates_removed = total_found - total_unique

    print(f"info: 🧐 Found {total_found} total occurrences, removed {duplicates_removed} duplicates.")

    # 4. Save only the unique keys to the output file
    save_keys_to_file(unique_keys)