import os
import re
import json
import commentjson
from uuid import uuid4

def extract_stiffness_matrix(response):
    # Define the pattern to extract the JSON code block
    pattern = r"```json\n(.*?)\n```"
    match = re.search(pattern, response, re.DOTALL)
    
    if match:
        json_code = match.group(1)
        try:
            # Parse the JSON code with comments
            data = commentjson.loads(json_code)
            stiffness_matrix = data.get('stiffness_matrix')
            if stiffness_matrix is None:
                print("Key 'stiffness_matrix' not found in JSON data.")
                return None
            
            # Validate the stiffness matrix structure
            if len(stiffness_matrix) != 3:
                print(f"Expected 3 rows in stiffness_matrix, found {len(stiffness_matrix)}.")
                return None
            for row in stiffness_matrix:
                if len(row) != 3:
                    print(f"Expected 3 values in row {row}, found {len(row)}.")
                    return None
            
            # Save stiffness matrix to a file in 'matrices' directory if valid
            if not os.path.exists("matrices"):
                os.makedirs("matrices")
            matrix_filename = f"{uuid4()}.json"
            matrix_file_path = f"matrices/{matrix_filename}"
            
            with open(matrix_file_path, "w") as matrix_file:
                json.dump(stiffness_matrix, matrix_file)
            
            # Generate URL for the matrix file
            matrix_file_url = f"https://matrices-sunbird-dashing.ngrok-free.app/matrices/{matrix_filename}"
            print("Stiffness matrix extracted and saved:", stiffness_matrix)
            
            return stiffness_matrix, matrix_file_url  # Return the URL directly

        except commentjson.JSONLibraryException as e:
            print(f"Error parsing JSON with comments: {e}")
            return None
    else:
        print("No JSON code block found in the response.")
        return None
