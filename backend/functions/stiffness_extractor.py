import re

def extract_stiffness_matrix(response_text):
    print("Extracting stiffness matrix...")
    # Find the position of "### Stiffness Matrix"
    matrix_header = "### Stiffness Matrix"
    start_index = response_text.find(matrix_header)
    if start_index == -1:
        print("Stiffness matrix header not found.")
        return None
    # Extract the text starting from the header
    text_after_header = response_text[start_index + len(matrix_header):]
    # Use regex to find the markdown table
    table_pattern = r"\|.*\n(?:\|.*\n)+"
    match = re.search(table_pattern, text_after_header)
    if not match:
        print("No table found after stiffness matrix header.")
        return None
    table_text = match.group()
    print("Table text found:")
    print(table_text)
    # Split the table into lines
    lines = table_text.strip().split('\n')
    # Skip the header and separator lines
    data_lines = [line for line in lines if re.match(r'\|\s*[\d.]+', line)]
    if len(data_lines) != 3:
        print(f"Expected 3 data rows, found {len(data_lines)}.")
        return None
    stiffness_matrix = []
    for line in data_lines:
        # Extract the numeric values from each line
        values = [v.strip() for v in line.strip('|').split('|')]
        if len(values) != 3:
            print(f"Unexpected number of values in line: {line}")
            return None
        try:
            row = [float(v) for v in values]
            stiffness_matrix.append(row)
        except ValueError as e:
            print(f"Error converting to float: {e}")
            return None
    print("Stiffness matrix extracted:", stiffness_matrix)
    return stiffness_matrix
