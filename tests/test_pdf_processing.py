#!/usr/bin/env python3
"""
Test PDF processing to see what's going wrong
"""
import sys
import os
sys.path.append('backend')

from backend.app.pdf_ingest import extract_text_from_pdf, chunk_text

def test_pdf_processing():
    """Test the PDF processing to see what's happening"""
    print("=== Testing PDF Processing ===\n")
    
    # Test with the PDF file
    pdf_files = [
        "data/milifestyle.pdf",
        "backend/data/milifestyle.pdf"
    ]
    
    pdf_path = None
    for path in pdf_files:
        if os.path.exists(path):
            pdf_path = path
            break
    
    if not pdf_path:
        print("❌ No milifestyle.pdf found in expected locations")
        print("Available files in data/:")
        if os.path.exists("data"):
            for f in os.listdir("data"):
                print(f"   • {f}")
        return False
    
    print(f"📄 Found PDF: {pdf_path}")
    
    # Extract text
    print("🔍 Extracting text...")
    text = extract_text_from_pdf(pdf_path)
    
    print(f"📊 Text extraction results:")
    print(f"   • Total length: {len(text)} characters")
    print(f"   • First 200 chars: {repr(text[:200])}")
    print(f"   • Last 200 chars: {repr(text[-200:])}")
    print()
    
    # Test chunking
    print("🔧 Testing chunking...")
    chunks = chunk_text(text, chunk_size=1200, overlap=200)
    
    print(f"📊 Chunking results:")
    print(f"   • Total chunks: {len(chunks)}")
    print()
    
    # Show first few chunks
    print("📋 First 3 chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n   Chunk {i}:")
        print(f"   Length: {len(chunk)} chars")
        print(f"   Content: {repr(chunk[:100])}...")
    
    # Test with different chunk sizes
    print(f"\n🧪 Testing different chunk sizes:")
    for chunk_size in [500, 800, 1200, 2000]:
        test_chunks = chunk_text(text, chunk_size=chunk_size, overlap=200)
        print(f"   • Chunk size {chunk_size}: {len(test_chunks)} chunks")
    
    return len(chunks) > 3

def test_manual_chunking():
    """Test with manual chunking approach"""
    print(f"\n=== Testing Manual Chunking ===\n")
    
    # Create some test text
    test_text = """Mi Lifestyle Marketing Global Private Limited is a direct selling company that deals with the distribution of quality products and services. The company has been established with the vision to provide products and services that fit exceedingly well on the quality barometer and is economical. Mi Lifestyle believes in building quality products, maintaining networks and facilitating sales. The company sets parameters like quality, affordability, and customer satisfaction as its core values. Mi Lifestyle Marketing Global Private Limited strives to provide the best products and services to its customers while maintaining the highest standards of quality and excellence."""
    
    print(f"📝 Test text length: {len(test_text)} characters")
    
    # Test different approaches
    chunks_1200 = chunk_text(test_text, chunk_size=1200, overlap=200)
    chunks_800 = chunk_text(test_text, chunk_size=800, overlap=200)
    chunks_500 = chunk_text(test_text, chunk_size=500, overlap=100)
    
    print(f"🧪 Chunking test results:")
    print(f"   • 1200 chars: {len(chunks_1200)} chunks")
    print(f"   • 800 chars: {len(chunks_800)} chunks")
    print(f"   • 500 chars: {len(chunks_500)} chunks")
    
    print(f"\n📋 500-char chunks:")
    for i, chunk in enumerate(chunks_500):
        print(f"   Chunk {i}: {len(chunk)} chars - {chunk[:60]}...")

if __name__ == "__main__":
    print("Starting PDF Processing Test...\n")
    
    success = test_pdf_processing()
    
    if not success:
        test_manual_chunking()
    
    print("\n=== Test Complete ===")
