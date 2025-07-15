import os
import json
import re


def transform_json_structure(json_data: dict) -> dict:
    result = json_data.copy()  # Copy the root structure
    network = json_data.get("network", {})
    # Transform the network section
    #transformed_network = {}
    for section_name, section in network.items():
        fields = section.get("fields", [])
        data = section.get("data", [])
        # If there are no fields or data, keep the section as is
        if not data:
            structured_data  = [dict(zip(fields, [None] * len(fields)))]
        # Ensure data is a list of lists
        elif isinstance(data[0], list):
            # Multiple rows of data
            structured_data = [dict(zip(fields, row)) for row in data]
        else:
            # Single row of data
            structured_data = [dict(zip(fields, data))]
        # update section with structured data
        result['network'][section_name] = structured_data
    return result


# Function to read JSON from a file, modify it, and write it back
def process_json_file(input_file, output_file):
    # Open the input JSON file and load its data
    with open(input_file, 'r') as infile:
        # Read raw text to preserve formatting
        #raw_text = infile.read()
        json_data = json.load(infile)
    # Convert the network structure
    converted_data = transform_json_structure(json_data)
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    # Write the modified data back to the output file
    with open(output_file, 'w') as outfile:
        json.dump(converted_data, outfile, indent=4)

if __name__ == '__main__':
    #
    files = [f for f in os.listdir('.') if f.endswith('.rawx')]
    for f in files:
        input_file = os.path.join('.', f)
        output_file = os.path.join('./processed_files', f)
        # Process each file
        process_json_file(input_file, output_file)
        print(f"Processed {input_file} and saved to {output_file}")
