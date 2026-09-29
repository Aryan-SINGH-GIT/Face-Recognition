import faiss
import numpy as np
import json
from pathlib import Path

class FaissManager:
    def __init__(self, index_path="index.faiss", mapping_path="identities.json", embedding_dim=512):
        self.index_path = Path(index_path)
        self.mapping_path = Path(mapping_path)
        self.embedding_dim = embedding_dim
        
        # Initialize index
        if self.index_path.exists() and self.mapping_path.exists():
            self.load()
        else:
            # Using L2 distance for Euclidean similarity
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.identities = [] # Maps faiss internal ID to identity string

    def add_embeddings(self, embeddings, labels):
        """Adds embeddings (numpy array) and their corresponding labels (list of strings)."""
        if len(embeddings) != len(labels):
            raise ValueError("Number of embeddings must match number of labels")
        
        if len(embeddings) == 0:
            return
            
        embeddings_np = np.array(embeddings).astype('float32')
        self.index.add(embeddings_np)
        self.identities.extend(labels)
        
    def search(self, query_embedding, k=1, threshold=1.0):
        """Searches for the closest embedding. Returns (identity, distance) or None if above threshold."""
        query_np = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_np, k)
        
        results = []
        for i in range(k):
            idx = indices[0][i]
            dist = distances[0][i]
            
            if idx != -1 and dist < threshold:
                identity = self.identities[idx]
                results.append((identity, float(dist)))
                
        return results

    def save(self):
        """Saves the index and the identity mapping to disk."""
        faiss.write_index(self.index, str(self.index_path))
        with open(self.mapping_path, 'w') as f:
            json.dump(self.identities, f)
            
    def load(self):
        """Loads the index and identity mapping from disk."""
        self.index = faiss.read_index(str(self.index_path))
        with open(self.mapping_path, 'r') as f:
            self.identities = json.load(f)

if __name__ == "__main__":
    # Simple test
    manager = FaissManager(embedding_dim=512)
    print(f"Initialized Faiss index with {manager.index.ntotal} embeddings.")
