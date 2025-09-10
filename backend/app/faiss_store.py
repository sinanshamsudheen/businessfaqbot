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
            self.index = faiss.read_index(index_file)
            with open(meta_file, "r") as f:
                self.meta = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(dim)  # Inner product similarity
            self.meta = []

    def add(self, texts: List[str], metas: List[dict]):
        """Add text embeddings to the FAISS index"""
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
        
        # Save index and metadata
        self.save()

    def query(self, text: str, k: int = 5):
        """Query the FAISS index for similar texts"""
        # Get embedding for query text
        embedding = get_embeddings([text])[0]
        
        # Convert to numpy array
        arr = np.array([embedding]).astype("float32")
        
        # Normalize for inner product similarity
        faiss.normalize_L2(arr)
        
        # Search index
        scores, ids = self.index.search(arr, k)
        
        # Format results
        results = []
        for idx, score in zip(ids[0], scores[0]):
            if idx < len(self.meta):
                results.append({
                    "meta": self.meta[idx], 
                    "score": float(score)
                })
        return results

    def save(self):
        """Save the FAISS index and metadata to disk"""
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, "w") as f:
            json.dump(self.meta, f)

    def __len__(self):
        """Return the number of vectors in the index"""
        return len(self.meta)