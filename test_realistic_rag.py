#!/usr/bin/env python3
"""
Test RAG functionality by mocking OpenAI to verify threshold fix
"""
import sys
import os
sys.path.append('backend')

import faiss
import numpy as np
import json

def simulate_real_embedding():
    """Create a realistic embedding that should match Mi Lifestyle content"""
    # Load actual embeddings to get a realistic query
    index = faiss.read_index("data/faiss.index")
    
    # Get the first vector from the index as our "realistic" query
    # This simulates what would happen with a real query about company content
    if index.ntotal > 0:
        # Reconstruct a vector from the index (this gives us a real embedding)
        sample_vector = index.reconstruct(0)  # Get first vector
        
        # Add some small random noise to simulate a slightly different but related query
        noise = np.random.normal(0, 0.1, sample_vector.shape)
        query_vector = sample_vector + noise
        
        # Normalize
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm
            
        return query_vector.reshape(1, -1).astype('float32')
    
    return None

def test_realistic_similarity_scores():
    """Test with realistic embeddings to see actual score ranges"""
    print("=== Testing Realistic Similarity Scores ===\n")
    
    # Load index and metadata
    index = faiss.read_index("data/faiss.index")
    with open("data/meta.json", "r") as f:
        metadata = json.load(f)
    
    print(f"📊 Testing with {index.ntotal} vectors\n")
    
    # Test multiple realistic scenarios
    test_scenarios = [
        "Exact match (same vector)",
        "Very similar (small noise)",
        "Somewhat similar (medium noise)", 
        "Different but related (large noise)"
    ]
    
    base_vector = index.reconstruct(0)  # Use first vector as base
    
    for i, scenario in enumerate(test_scenarios):
        print(f"🔍 {scenario}:")
        
        if i == 0:  # Exact match
            query_vector = base_vector.copy()
        else:  # Add increasing amounts of noise
            noise_level = i * 0.2
            noise = np.random.normal(0, noise_level, base_vector.shape)
            query_vector = base_vector + noise
        
        # Normalize
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm
        
        query_vector = query_vector.reshape(1, -1).astype('float32')
        
        # Search
        scores, indices = index.search(query_vector, 5)
        
        print(f"   Top 5 scores: {[f'{s:.3f}' for s in scores[0]]}")
        
        # Test different thresholds
        thresholds = [0.015, 0.05, 0.1, 0.2]
        for threshold in thresholds:
            passed = scores[0][0] >= threshold
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   Threshold {threshold}: {status}")
        
        print()

def test_company_name_scenario():
    """Simulate what happens when someone asks 'what is the name of the company'"""
    print("=== Testing 'Company Name' Query Scenario ===\n")
    
    # Load everything
    index = faiss.read_index("data/faiss.index")
    with open("data/meta.json", "r") as f:
        metadata = json.load(f)
    
    # Find chunks that mention the company name
    company_chunks = []
    for i, meta in enumerate(metadata):
        text = meta.get('text', '').lower()
        if 'mi lifestyle' in text or 'marketing global' in text:
            company_chunks.append((i, meta))
    
    print(f"📋 Found {len(company_chunks)} chunks mentioning company name")
    
    if company_chunks:
        print("\nSample company-related chunks:")
        for i, (idx, meta) in enumerate(company_chunks[:3]):
            text_preview = meta.get('text', '')[:100] + "..."
            print(f"   {i+1}. Index {idx}: {text_preview}")
        
        # Test similarity with company-related content
        print(f"\n🔍 Testing similarity using company chunk {company_chunks[0][0]}:")
        
        # Use a company chunk as query
        company_vector = index.reconstruct(company_chunks[0][0])
        
        # Add slight variation to simulate a real query
        noise = np.random.normal(0, 0.1, company_vector.shape)
        query_vector = company_vector + noise
        
        # Normalize
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm
        
        query_vector = query_vector.reshape(1, -1).astype('float32')
        
        # Search
        scores, indices = index.search(query_vector, 10)
        
        print(f"   Top 10 scores: {[f'{s:.3f}' for s in scores[0]]}")
        
        # Check which threshold would work
        best_score = scores[0][0]
        print(f"\n   Best score: {best_score:.3f}")
        
        recommended_threshold = max(0.01, best_score * 0.3)  # 30% of best score, minimum 0.01
        print(f"   Recommended threshold: {recommended_threshold:.3f}")
        
        # Test current threshold
        current_threshold = 0.015
        would_pass = best_score >= current_threshold
        status = "✅ PASS" if would_pass else "❌ FAIL"
        print(f"   Current threshold (0.015): {status}")

if __name__ == "__main__":
    print("Starting Realistic RAG Test...\n")
    
    test_realistic_similarity_scores()
    test_company_name_scenario()
    
    print("\n=== Test Complete ===")
