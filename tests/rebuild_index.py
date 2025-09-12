#!/usr/bin/env python3
"""
Properly rebuild the FAISS index with all PDFs and better chunking
"""
import sys
import os
sys.path.append('backend')

from backend.app.pdf_ingest import extract_text_from_pdf, chunk_text
from backend.app.faiss_store import FaissStore
import json

def rebuild_comprehensive_index():
    """Rebuild FAISS index with all PDFs and optimized chunking"""
    print("=== Rebuilding Comprehensive FAISS Index ===\n")
    
    # PDF files to process
    pdf_directory = "backend/data"
    pdf_files = [
        "DSguidelines.pdf",
        "micontactus.pdf", 
        "milifestyle.pdf",
        "mipolicies.pdf"
    ]
    
    # Use smaller chunks for better granularity
    chunk_size = 600  # Smaller chunks
    overlap = 100     # Smaller overlap
    
    print(f"📊 Configuration:")
    print(f"   • Chunk size: {chunk_size} characters")
    print(f"   • Overlap: {overlap} characters")
    print(f"   • PDF files: {len(pdf_files)}")
    print()
    
    # Collect all chunks and metadata
    all_texts = []
    all_metadata = []
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            continue
        
        print(f"📄 Processing: {pdf_file}")
        
        # Extract text
        text = extract_text_from_pdf(pdf_path)
        print(f"   • Extracted: {len(text)} characters")
        
        # Clean text more thoroughly
        import re
        # Remove excessive whitespace but preserve paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve paragraph breaks
        text = re.sub(r'[ \t]+', ' ', text)      # Normalize spaces/tabs
        text = text.strip()
        
        # Chunk text
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        print(f"   • Created: {len(chunks)} chunks")
        
        # Create metadata for each chunk
        for i, chunk in enumerate(chunks):
            # Skip very short chunks
            if len(chunk.strip()) < 50:
                continue
                
            all_texts.append(chunk.strip())
            all_metadata.append({
                "source": pdf_file,
                "chunk_id": i,
                "text": chunk.strip(),
                "char_count": len(chunk.strip())
            })
        
        print(f"   • Added: {len([c for c in chunks if len(c.strip()) >= 50])} valid chunks")
        print()
    
    print(f"📊 Total collection:")
    print(f"   • Total chunks: {len(all_texts)}")
    print(f"   • Total metadata: {len(all_metadata)}")
    
    if len(all_texts) == 0:
        print("❌ No chunks to process!")
        return False
    
    # Create new FAISS store
    print(f"\n🔧 Creating new FAISS index...")
    
    # Backup existing index
    if os.path.exists("data/faiss.index"):
        backup_suffix = "_backup_rebuild"
        os.rename("data/faiss.index", f"data/faiss.index{backup_suffix}")
        os.rename("data/meta.json", f"data/meta.json{backup_suffix}")
        print(f"   • Backed up existing index with suffix '{backup_suffix}'")
    
    # Create new store and add all documents at once
    faiss_store = FaissStore()
    
    print(f"   • Adding {len(all_texts)} chunks to FAISS...")
    faiss_store.add(all_texts, all_metadata)
    
    print(f"✅ Index rebuilt successfully!")
    
    # Test the new index
    print(f"\n🔍 Testing new index:")
    
    stats = faiss_store.get_stats()
    print(f"   • Vectors: {stats['total_vectors']}")
    print(f"   • Metadata: {stats['metadata_count']}")
    
    # Test search diversity
    test_query = "Mi Lifestyle company"
    results = faiss_store.query(test_query, k=5)
    
    print(f"   • Test query: '{test_query}'")
    print(f"   • Results: {len(results)}")
    
    if results:
        scores = [r['score'] for r in results]
        unique_scores = len(set(scores))
        print(f"   • Score diversity: {unique_scores}/{len(scores)} unique")
        print(f"   • Score range: {min(scores):.3f} to {max(scores):.3f}")
        
        # Show source diversity
        sources = [r['meta']['source'] for r in results]
        unique_sources = len(set(sources))
        print(f"   • Source diversity: {unique_sources} different sources")
    
    # Show summary by source
    print(f"\n📊 Final summary by source:")
    source_counts = {}
    for meta in all_metadata:
        source = meta['source']
        source_counts[source] = source_counts.get(source, 0) + 1
    
    for source, count in sorted(source_counts.items()):
        print(f"   • {source}: {count} chunks")
    
    return True

if __name__ == "__main__":
    print("Starting Comprehensive Index Rebuild...\n")
    
    success = rebuild_comprehensive_index()
    
    if success:
        print("\n🎉 Comprehensive index rebuild completed!")
        print("Your RAG system now has much more content to work with.")
    else:
        print("\n❌ Index rebuild failed")
    
    print("\n=== Rebuild Complete ===")
