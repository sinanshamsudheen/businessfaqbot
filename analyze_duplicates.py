#!/usr/bin/env python3
"""
Investigate and fix duplicate embeddings issue
"""
import sys
import os
sys.path.append('backend')

import faiss
import numpy as np
import json
from collections import defaultdict

def analyze_duplicates():
    """Analyze the FAISS index for duplicate embeddings"""
    print("=== Analyzing FAISS Index for Duplicates ===\n")
    
    # Load index and metadata
    index = faiss.read_index("data/faiss.index")
    with open("data/meta.json", "r") as f:
        metadata = json.load(f)
    
    print(f"📊 Index Stats:")
    print(f"   • Total vectors: {index.ntotal}")
    print(f"   • Metadata entries: {len(metadata)}")
    print()
    
    # Check for duplicate metadata
    text_counts = defaultdict(int)
    source_counts = defaultdict(int)
    
    for meta in metadata:
        text = meta.get('text', '')
        source = meta.get('source', '')
        text_counts[text] += 1
        source_counts[source] += 1
    
    # Find duplicates
    duplicate_texts = {text: count for text, count in text_counts.items() if count > 1}
    
    print(f"📋 Duplicate Analysis:")
    print(f"   • Unique texts: {len(text_counts)}")
    print(f"   • Duplicate texts: {len(duplicate_texts)}")
    
    if duplicate_texts:
        print(f"\n   Top duplicates:")
        sorted_dupes = sorted(duplicate_texts.items(), key=lambda x: x[1], reverse=True)
        for text, count in sorted_dupes[:5]:
            preview = text[:60] + "..." if len(text) > 60 else text
            print(f"      • {count}x: {preview}")
    
    print(f"\n   Sources:")
    for source, count in source_counts.items():
        print(f"      • {source}: {count} chunks")
    
    # Check if vectors are actually identical
    print(f"\n🔍 Vector Analysis:")
    
    # Sample a few vectors and check for exact duplicates
    if index.ntotal >= 2:
        vec1 = index.reconstruct(0)
        vec2 = index.reconstruct(1)
        
        # Check if they're identical
        if np.allclose(vec1, vec2, atol=1e-6):
            print("   ❌ Vectors 0 and 1 are identical!")
        else:
            print("   ✅ Vectors 0 and 1 are different")
            
        # Check similarity between different vectors
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)
        similarity = np.dot(vec1_norm, vec2_norm)
        print(f"   • Similarity between vec 0 and 1: {similarity:.3f}")
        
        # Check a few more
        similarities = []
        for i in range(min(10, index.ntotal-1)):
            vec_a = index.reconstruct(i)
            vec_b = index.reconstruct(i+1)
            vec_a_norm = vec_a / np.linalg.norm(vec_a)
            vec_b_norm = vec_b / np.linalg.norm(vec_b)
            sim = np.dot(vec_a_norm, vec_b_norm)
            similarities.append(sim)
        
        print(f"   • Avg similarity between consecutive vectors: {np.mean(similarities):.3f}")
        print(f"   • Min similarity: {min(similarities):.3f}")
        print(f"   • Max similarity: {max(similarities):.3f}")

def test_unique_query():
    """Test with a completely unique query to see real performance"""
    print("\n=== Testing with Unique Content Query ===\n")
    
    # Load index
    index = faiss.read_index("data/faiss.index")
    with open("data/meta.json", "r") as f:
        metadata = json.load(f)
    
    # Create a query that's different from any content
    # We'll use a mix of different vectors to create something new
    if index.ntotal >= 3:
        vec1 = index.reconstruct(0)
        vec2 = index.reconstruct(index.ntotal//2)  # Middle vector
        vec3 = index.reconstruct(index.ntotal-1)   # Last vector
        
        # Create a weighted combination
        unique_query = 0.5 * vec1 + 0.3 * vec2 + 0.2 * vec3
        
        # Add some random noise
        noise = np.random.normal(0, 0.1, unique_query.shape)
        unique_query = unique_query + noise
        
        # Normalize
        unique_query = unique_query / np.linalg.norm(unique_query)
        unique_query = unique_query.reshape(1, -1).astype('float32')
        
        # Search
        scores, indices = index.search(unique_query, 10)
        
        print(f"🔍 Unique query results:")
        print(f"   Top 10 scores: {[f'{s:.3f}' for s in scores[0]]}")
        
        # Show diversity of results
        unique_sources = set()
        for idx in indices[0][:5]:
            if idx != -1 and idx < len(metadata):
                source = metadata[idx].get('source', 'Unknown')
                unique_sources.add(source)
        
        print(f"   Sources in top 5: {len(unique_sources)}")
        print(f"   Score range: {scores[0][-1]:.3f} to {scores[0][0]:.3f}")

if __name__ == "__main__":
    print("Starting Duplicate Analysis...\n")
    
    analyze_duplicates()
    test_unique_query()
    
    print("\n=== Analysis Complete ===")
