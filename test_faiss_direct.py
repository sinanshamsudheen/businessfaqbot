#!/usr/bin/env python3
"""
Test script to verify FAISS store without needing OpenAI API
"""
import sys
import os
import json
sys.path.append('backend')

import faiss
import numpy as np

def test_faiss_direct():
    """Test FAISS store directly without OpenAI dependencies"""
    print("=== Testing FAISS Store Directly ===\n")
    
    # Load existing index
    index_file = "data/faiss.index"
    meta_file = "data/meta.json"
    
    if not os.path.exists(index_file) or not os.path.exists(meta_file):
        print("❌ No FAISS index found")
        return False
    
    # Load index and metadata
    index = faiss.read_index(index_file)
    with open(meta_file, "r") as f:
        metadata = json.load(f)
    
    print(f"📊 FAISS Index Stats:")
    print(f"   • Total vectors: {index.ntotal}")
    print(f"   • Metadata entries: {len(metadata)}")
    print(f"   • Index type: {type(index).__name__}")
    print(f"   • Is trained: {index.is_trained}")
    print()
    
    # Sample some metadata to understand content
    print("📄 Sample Documents:")
    for i, meta in enumerate(metadata[:3]):
        source = meta.get('source', 'Unknown')
        text_preview = meta.get('text', '')[:100] + "..."
        chunk_id = meta.get('chunk_id', 'N/A')
        print(f"   {i+1}. Source: {source} | Chunk: {chunk_id}")
        print(f"      Text: {text_preview}")
        print()
    
    # Test with random query vector (just to test similarity search)
    print("🔍 Testing similarity search with random vector:")
    
    # Create a random query vector with same dimension
    query_vector = np.random.rand(1, 1536).astype('float32')
    faiss.normalize_L2(query_vector)  # Normalize like real embeddings
    
    # Search
    k = min(5, index.ntotal)
    scores, indices = index.search(query_vector, k)
    
    print(f"   Found {len(scores[0])} results:")
    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        if idx == -1:
            continue
        if idx < len(metadata):
            source = metadata[idx].get('source', 'Unknown')
            print(f"   {i+1}. Score: {score:.3f} | Index: {idx} | Source: {source}")
    
    print()
    
    # Check for potential issues
    print("🔍 Diagnostics:")
    
    # Check score distribution with multiple random queries
    all_scores = []
    for _ in range(10):
        rand_query = np.random.rand(1, 1536).astype('float32')
        faiss.normalize_L2(rand_query)
        scores, _ = index.search(rand_query, min(10, index.ntotal))
        all_scores.extend(scores[0].tolist())
    
    if all_scores:
        print(f"   • Score range: {min(all_scores):.3f} to {max(all_scores):.3f}")
        print(f"   • Average score: {sum(all_scores)/len(all_scores):.3f}")
        
        # Count how many scores are above different thresholds
        above_02 = sum(1 for s in all_scores if s > 0.2)
        above_03 = sum(1 for s in all_scores if s > 0.3)
        above_05 = sum(1 for s in all_scores if s > 0.5)
        
        print(f"   • Scores > 0.2: {above_02}/{len(all_scores)} ({above_02/len(all_scores)*100:.1f}%)")
        print(f"   • Scores > 0.3: {above_03}/{len(all_scores)} ({above_03/len(all_scores)*100:.1f}%)")
        print(f"   • Scores > 0.5: {above_05}/{len(all_scores)} ({above_05/len(all_scores)*100:.1f}%)")
    
    print()
    
    # Check metadata consistency
    sources = {}
    for meta in metadata:
        source = meta.get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print(f"📊 Documents by source:")
    for source, count in sorted(sources.items()):
        print(f"   • {source}: {count} chunks")
    
    return True

if __name__ == "__main__":
    print("Starting FAISS Direct Test...\n")
    test_faiss_direct()
    print("\n=== Test Complete ===")
