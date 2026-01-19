import csv
import zipfile
import io
import sys
import os

def find_csv_in_zip(zip_path):
    """
    Finds the first CSV file in a zip archive.

    Args:
        zip_path (str): The path to the zip file.

    Returns:
        str: The name of the first CSV file found, or None.
    """
    with zipfile.ZipFile(zip_path, 'r') as z:
        for filename in z.namelist():
            if filename.endswith('.csv'):
                return filename
    return None

def extract_question_responses(zip_path, csv_name, column_name):
    """
    Extracts a column from a CSV file inside a zip archive.

    Args:
        zip_path (str): The path to the zip file.
        csv_name (str): The name of the CSV file inside the zip archive.
        column_name (str): The name of the column to extract.

    Returns:
        list: A list of strings from the specified column.
    """
    responses = []
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(csv_name, 'r') as f:
            reader = csv.DictReader(io.TextIOWrapper(f, 'utf-8'))
            for row in reader:
                if column_name in row:
                    responses.append(row[column_name])
    return [r.replace('\n', ' ')
            for r in responses
            if r is not None
            and len(r) > len('presenter') + 3]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_responses.py <zip_file_path>")
        sys.exit(1)

    zip_file_path = sys.argv[1]
    
    if not os.path.exists(zip_file_path):
        print(f"Error: Zip file not found at '{zip_file_path}'")
        sys.exit(1)

    csv_file_name = find_csv_in_zip(zip_file_path)

    if not csv_file_name:
        print(f"No CSV file found in '{zip_file_path}'")
        sys.exit(1)

    column_to_extract = 'Question 1 Response'
    
    responses_list = extract_question_responses(zip_file_path, csv_file_name, column_to_extract)
    print('\n'.join(responses_list))
