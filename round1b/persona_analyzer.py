from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import fitz
import json
import os
from datetime import datetime

# Load model (pre-downloaded in Docker build)
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

def get_embedding(text):
    """Get text embedding with caching"""
    if not text.strip():
        return np.zeros(384)
    return model.encode([text], convert_to_tensor=False)[0]

def rank_sections(documents, persona, job):
    """Rank sections based on persona and job"""
    query = f"Persona: {persona}\nTask: {job}"
    query_embedding = get_embedding(query)
    
    section_data = []
    for doc in documents:
        for section in doc["outline"]:
            # Get full section text
            full_text = extract_section_text(doc["path"], section["page"])
            embedding = get_embedding(section["text"] + " " + full_text[:500])
            similarity = cosine_similarity([query_embedding], [embedding])[0][0]
            
            section_data.append({
                "document": os.path.basename(doc["path"]),
                "page": section["page"],
                "section_title": section["text"],
                "similarity": similarity,
                "full_text": full_text
            })
    
    # Rank by similarity
    section_data.sort(key=lambda x: x["similarity"], reverse=True)
    
    # Add importance rank
    for i, item in enumerate(section_data):
        item["importance_rank"] = i + 1
    
    return section_data[:50]  # Return top 50 sections

def extract_section_text(pdf_path, page_num):
    """Extract text from specific page"""
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]
        return page.get_text("text")
    except:
        return ""

def extract_key_sentences(text, max_sentences=3):
    """Extract key sentences using TF-IDF heuristic"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    import nltk
    
    sentences = nltk.sent_tokenize(text)
    if len(sentences) <= max_sentences:
        return sentences
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)
    sentence_scores = tfidf_matrix.sum(axis=1)
    
    top_indices = np.argsort(-sentence_scores.A1)[:max_sentences]
    return [sentences[i] for i in sorted(top_indices)]

def process_documents(input_dir, persona, job):
    """Process all documents in directory"""
    documents = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            title, outline = extract_outline(pdf_path)  # From Round1A
            documents.append({
                "path": pdf_path,
                "filename": filename,
                "title": title,
                "outline": outline
            })
    return documents

# Reuse Round1A extraction logic
def extract_outline(pdf_path):
    # Simplified version from Round1A
    doc = fitz.open(pdf_path)
    title = doc.metadata.get("title", "Untitled")
    outline = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks", sort=True)
        for block in blocks:
            text = block[4].strip()
            if len(text) > 30 or len(text) < 3:
                continue
            if block[6] == 0:  # Heading type
                level = f"H{min(block[5] + 1, 3)}"  # Convert to H1-H3
                outline.append({
                    "level": level,
                    "text": text,
                    "page": page_num + 1
                })
    return title, outline