import faiss
import numpy as np
import os
import json
from typing import List
from .embeddings_provider import get_embeddings

class FaissStore:
    def __init__(self, dim: int = 1536, index_file: str = "data/faiss.index", meta_file: str = "data/meta.json"):
        self.dim = dim
        self.index_file = index_file
        self.meta_file = meta_file
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(index_file), exist_ok=True)
        
        if os.path.exists(index_file) and os.path.exists(meta_file):
            print(f"Loading existing FAISS index from {index_file}")
            self.index = faiss.read_index(index_file)
            with open(meta_file, "r") as f:
                self.meta = json.load(f)
            print(f"Loaded index with {self.index.ntotal} vectors and {len(self.meta)} metadata entries")
            
            # Check for consistency
            if self.index.ntotal != len(self.meta):
                print(f"Warning: Index has {self.index.ntotal} vectors but metadata has {len(self.meta)} entries")
        else:
            print("Creating new FAISS index...")
            self.index = faiss.IndexFlatIP(dim)  # Inner product similarity
            self.meta = []

    def add(self, texts: List[str], metas: List[dict]):
        """Add text embeddings to the FAISS index"""
        if not texts or not metas:
            print("No texts or metadata to add")
            return
            
        if len(texts) != len(metas):
            print(f"Mismatch: {len(texts)} texts vs {len(metas)} metadata entries")
            return
            
        print(f"Adding {len(texts)} documents to FAISS index...")
        
        # Get embeddings for texts
        embeddings = get_embeddings(texts)
        
        # Convert to numpy array
        arr = np.array(embeddings).astype("float32")
        
        # Normalize for inner product similarity
        faiss.normalize_L2(arr)
        
        # Add to index
        self.index.add(arr)
        
        # Add metadata
        self.meta.extend(metas)
        
        print(f"Added {len(texts)} documents. Total vectors: {self.index.ntotal}")
        
        # Save index and metadata
        self.save()

    def query(self, text: str, k: int = 5):
        """Query the FAISS index for similar texts"""
        if self.index.ntotal == 0:
            print("Index is empty")
            return []
            
        # Get embedding for query text
        embedding = get_embeddings([text])[0]
        
        # Convert to numpy array
        arr = np.array([embedding]).astype("float32")
        
        # Normalize for inner product similarity
        faiss.normalize_L2(arr)
        
        # Adjust k to not exceed available documents
        k = min(k, self.index.ntotal)
        
        # Search index
        scores, ids = self.index.search(arr, k)
        
        # Format results
        results = []
        for idx, score in zip(ids[0], scores[0]):
            if idx == -1:  # FAISS returns -1 for invalid results
                continue
                
            if idx < len(self.meta):
                results.append({
                    "meta": self.meta[idx], 
                    "score": float(score)
                })
            else:
                print(f"Warning: Index {idx} exceeds metadata length {len(self.meta)}")
        
        # Sort by score (higher is better for inner product)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"Query returned {len(results)} results")
        if results:
            print(f"Top score: {results[0]['score']:.3f}")
            
        return results

    def save(self):
        """Save the FAISS index and metadata to disk"""
        try:
            faiss.write_index(self.index, self.index_file)
            with open(self.meta_file, "w") as f:
                json.dump(self.meta, f, ensure_ascii=False, indent=2)
            print(f"Saved index with {self.index.ntotal} vectors to {self.index_file}")
        except Exception as e:
            print(f"Error saving index: {e}")

    def get_stats(self):
        """Get statistics about the index"""
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dim,
            'metadata_count': len(self.meta),
            'index_type': type(self.index).__name__ if self.index else None
        }

    def __len__(self):
        """Return the number of vectors in the index"""
        return len(self.meta)