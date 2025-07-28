import os
import json
from pdf_processor import extract_outline

def process_directory(input_dir, output_dir):
    """Process all PDFs in input directory"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            try:
                title, outline = extract_outline(pdf_path)
                output_data = {
                    "title": title,
                    "outline": outline
                }
                json_path = os.path.join(
                    output_dir, 
                    os.path.splitext(filename)[0] + ".json"
                )
                with open(json_path, "w") as f:
                    json.dump(output_data, f, indent=2)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    input_dir = "/app/input"
    output_dir = "/app/output"
    process_directory(input_dir, output_dir)