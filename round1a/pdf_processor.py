import fitz
import pdfplumber
import re
import json
import os
from collections import defaultdict

def get_font_stats(pdf_path):
    """Analyze font usage statistics"""
    font_stats = defaultdict(int)
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for char in page.chars:
                font_stats[(char["size"], char["fontname"])] += 1
    return font_stats

def extract_outline(pdf_path):
    """Extract title and headings from PDF"""
    doc = fitz.open(pdf_path)
    font_stats = get_font_stats(pdf_path)
    
    # Get top 3 most common fonts
    common_fonts = sorted(font_stats.items(), key=lambda x: x[1], reverse=True)[:3]
    common_sizes = {size for (size, _), _ in common_fonts}
    max_common_size = max(common_sizes) if common_sizes else 12
    
    # Extract title from first page
    first_page = doc[0]
    blocks = first_page.get_text("blocks", sort=True)
    title = "Untitled Document"
    if blocks:
        title_block = max(blocks[:5], key=lambda b: b[4])
        title = title_block[4].replace("\n", " ").strip()
    
    outline = []
    heading_pattern = re.compile(r'^(chapter|section|part|appendix|\d+\.\d+)', re.IGNORECASE)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_width = page.rect.width
        
        with pdfplumber.open(pdf_path) as pdf:
            plumber_page = pdf.pages[page_num]
            words = plumber_page.extract_words(extra_attrs=["fontname", "size"])
            
            # Group words into lines
            lines = defaultdict(list)
            for word in words:
                y = round(word["top"])
                lines[y].append(word)
            
            # Process each line
            for y, words in sorted(lines.items()):
                if not words: 
                    continue
                    
                # Skip header/footer regions
                if y < 50 or y > plumber_page.height - 50:
                    continue
                    
                # Get line properties
                text = " ".join(w["text"] for w in words)
                font_size = max(w["size"] for w in words)
                font_name = max(set(w["fontname"] for w in words), 
                               key=lambda x: sum(1 for w in words if w["fontname"] == x))
                
                # Skip page numbers and small text
                if len(text) < 3 or text.isdigit() or font_size < 10:
                    continue
                
                # Calculate heading confidence
                size_ratio = font_size / max_common_size
                is_large = size_ratio > 1.5
                is_bold = "bold" in font_name.lower()
                is_centered = abs(0.5 - (words[0]["x0"] / page_width)) < 0.2
                matches_pattern = bool(heading_pattern.match(text))
                
                # Determine if heading
                if (is_large or is_bold or matches_pattern) and len(text.split()) < 15:
                    # Classify heading level
                    if size_ratio > 2.0 or is_centered:
                        level = "H1"
                    elif size_ratio > 1.7:
                        level = "H2"
                    else:
                        level = "H3"
                    
                    outline.append({
                        "level": level,
                        "text": text.strip(),
                        "page": page_num + 1
                    })
    
    return title, outline