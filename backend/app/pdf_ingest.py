from typing import List
import os
from PyPDF2 import PdfReader
import re

def extract_text_from_pdf(path: str) -> str:
    """Extract text from a PDF file"""
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start >= len(text):
            break
    return chunks

def process_pdf(file_path: str, faiss_store, chunk_size: int = 1200, overlap: int = 200):
    """Process a PDF file, chunk it, and add to FAISS store"""
    # Extract text from PDF
    text = extract_text_from_pdf(file_path)
    
    # Clean text
    text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespaces with single space
    text = text.strip()
    
    # Chunk text
    chunks = chunk_text(text, chunk_size, overlap)
    
    # Add chunks to FAISS store
    for i, chunk in enumerate(chunks):
        metadata = {
            "source": os.path.basename(file_path),
            "chunk_id": i,
            "text": chunk
        }
        faiss_store.add([chunk], [metadata])
    
    return len(chunks)