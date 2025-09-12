#!/usr/bin/env python3
"""
Clean and rebuild the FAISS index by removing duplicates
"""
import sys
import os
sys.path.append('backend')

import faiss
import numpy as np
import json
from collections import defaultdict

def clean_and_rebuild_index():
    """Remove duplicates and rebuild FAISS index"""
    print("=== Cleaning and Rebuilding FAISS Index ===\n")
    
    # Load current index and metadata
    index = faiss.read_index("data/faiss.index")
    with open("data/meta.json", "r") as f:
        metadata = json.load(f)
    
    print(f"📊 Current state:")
    print(f"   • Total vectors: {index.ntotal}")
    print(f"   • Metadata entries: {len(metadata)}")
    
    # Find unique texts and their first occurrence
    seen_texts = {}
    unique_indices = []
    unique_metadata = []
    
    for i, meta in enumerate(metadata):
        text = meta.get('text', '')
        
        if text not in seen_texts:
            seen_texts[text] = i
            unique_indices.append(i)
            unique_metadata.append(meta)
    
    print(f"\n🧹 After deduplication:")
    print(f"   • Unique texts: {len(unique_indices)}")
    print(f"   • Removed duplicates: {len(metadata) - len(unique_indices)}")
    
    # Extract unique vectors
    unique_vectors = []
    for idx in unique_indices:
        vector = index.reconstruct(idx)
        unique_vectors.append(vector)
    
    unique_vectors = np.array(unique_vectors).astype('float32')
    
    # Normalize vectors
    faiss.normalize_L2(unique_vectors)
    
    # Create new index
    new_index = faiss.IndexFlatIP(1536)
    new_index.add(unique_vectors)
    
    print(f"\n✅ New index created:")
    print(f"   • Vectors: {new_index.ntotal}")
    print(f"   • Metadata entries: {len(unique_metadata)}")
    
    # Test the new index
    print(f"\n🔍 Testing new index:")
    
    # Use first vector as query
    query_vector = unique_vectors[0:1].copy()
    scores, indices = new_index.search(query_vector, min(5, new_index.ntotal))
    
    print(f"   • Top 5 scores: {[f'{s:.3f}' for s in scores[0]]}")
    print(f"   • Score diversity: {len(set(scores[0]))} unique scores out of {len(scores[0])}")
    
    # Save the cleaned index
    backup_suffix = "_backup_duplicate"
    print(f"\n💾 Saving cleaned index:")
    
    # Backup original files
    os.rename("data/faiss.index", f"data/faiss.index{backup_suffix}")
    os.rename("data/meta.json", f"data/meta.json{backup_suffix}")
    print(f"   • Backed up original files with suffix '{backup_suffix}'")
    
    # Save new clean files
    faiss.write_index(new_index, "data/faiss.index")
    with open("data/meta.json", "w") as f:
        json.dump(unique_metadata, f, ensure_ascii=False, indent=2)
    
    print(f"   • Saved clean index: {new_index.ntotal} vectors")
    print(f"   • Saved clean metadata: {len(unique_metadata)} entries")
    
    # Final verification
    print(f"\n✅ Verification:")
    test_index = faiss.read_index("data/faiss.index")
    with open("data/meta.json", "r") as f:
        test_metadata = json.load(f)
    
    print(f"   • Loaded index: {test_index.ntotal} vectors")
    print(f"   • Loaded metadata: {len(test_metadata)} entries")
    
    # Test final similarity search diversity
    query = test_index.reconstruct(0).reshape(1, -1)
    scores, indices = test_index.search(query, min(5, test_index.ntotal))
    unique_scores = len(set(scores[0]))
    
    print(f"   • Score diversity test: {unique_scores}/{len(scores[0])} unique scores")
    
    if unique_scores > 1:
        print("   ✅ Index has diverse similarity scores!")
    else:
        print("   ❌ Still getting identical scores - may need different approach")
    
    return True

if __name__ == "__main__":
    print("Starting Index Cleanup...\n")
    
    success = clean_and_rebuild_index()
    
    if success:
        print("\n🎉 Index cleanup completed successfully!")
        print("\nNow the RAG system should work properly with diverse similarity scores.")
    else:
        print("\n❌ Index cleanup failed")
    
    print("\n=== Cleanup Complete ===")
