import os
import json
import argparse
from persona_analyzer import process_documents, rank_sections, extract_key_sentences
from datetime import datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--persona", type=str, required=True)
    parser.add_argument("--job", type=str, required=True)
    args = parser.parse_args()
    
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process documents
    documents = process_documents(input_dir, args.persona, args.job)
    ranked_sections = rank_sections(documents, args.persona, args.job)
    
    # Prepare output
    output = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in documents],
            "persona": args.persona,
            "job": args.job,
            "processing_timestamp": datetime.utcnow().isoformat()
        },
        "extracted_sections": [],
        "sub_sections": []
    }
    
    for section in ranked_sections:
        output["extracted_sections"].append({
            "document": section["document"],
            "page": section["page"],
            "section_title": section["section_title"],
            "importance_rank": section["importance_rank"]
        })
        
        # Extract key subsections
        key_sentences = extract_key_sentences(section["full_text"])
        for i, sentence in enumerate(key_sentences):
            output["sub_sections"].append({
                "document": section["document"],
                "text": sentence,
                "page": section["page"],
                "relevance_score": float(section["similarity"] * (1 - i*0.1))
            })
    
    # Save output
    output_path = os.path.join(output_dir, "output.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()