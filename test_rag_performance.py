#!/usr/bin/env python3
"""
Test script to verify RAG performance with the fixed configuration
"""
import sys
import os
sys.path.append('backend')

from backend.app.faiss_store import FaissStore
from backend.app.rag import query_rag

def test_basic_functionality():
    """Test basic RAG functionality"""
    print("=== Testing RAG Performance ===\n")
    
    # Initialize FAISS store
    faiss_store = FaissStore()
    
    # Get stats
    stats = faiss_store.get_stats()
    print(f"📊 FAISS Store Stats:")
    print(f"   • Total vectors: {stats['total_vectors']}")
    print(f"   • Metadata count: {stats['metadata_count']}")
    print(f"   • Index type: {stats['index_type']}")
    print(f"   • Dimension: {stats['dimension']}")
    print()
    
    if stats['total_vectors'] == 0:
        print("❌ No data in FAISS store. Please add some documents first.")
        return False
    
    # Test basic queries
    test_queries = [
        "What is the name of the company?",
        "Mi Lifestyle",
        "company name",
        "what products do you sell?",
        "business opportunity"
    ]
    
    print("🔍 Testing queries:\n")
    
    for query in test_queries:
        print(f"Query: '{query}'")
        try:
            answer, sources, _ = query_rag(query, faiss_store, top_k=5)
            
            # Check if we got a meaningful response
            if "I don't have that info" in answer:
                print(f"   ❌ No relevant information found")
            else:
                print(f"   ✅ Found answer ({len(sources)} sources)")
                # Show first few words of answer
                preview = answer[:100] + "..." if len(answer) > 100 else answer
                print(f"   Preview: {preview}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("-" * 50)
    
    return True

def test_similarity_thresholds():
    """Test different similarity thresholds"""
    print("\n=== Testing Similarity Search ===\n")
    
    faiss_store = FaissStore()
    
    # Test a simple query and show raw scores
    query = "company name"
    print(f"Testing query: '{query}'\n")
    
    try:
        results = faiss_store.query(query, k=10)
        
        print(f"Raw search results ({len(results)} found):")
        for i, result in enumerate(results[:5], 1):
            score = result['score']
            source = result['meta'].get('source', 'Unknown')
            text_preview = result['meta'].get('text', '')[:80] + "..."
            
            print(f"  {i}. Score: {score:.3f} | Source: {source}")
            print(f"     Text: {text_preview}")
            print()
        
        # Show score distribution
        if results:
            scores = [r['score'] for r in results]
            print(f"Score range: {min(scores):.3f} to {max(scores):.3f}")
            print(f"Average score: {sum(scores)/len(scores):.3f}")
        
    except Exception as e:
        print(f"❌ Error during similarity search: {e}")

if __name__ == "__main__":
    print("Starting RAG Performance Test...\n")
    
    success = test_basic_functionality()
    
    if success:
        test_similarity_thresholds()
    
    print("\n=== Test Complete ===")
