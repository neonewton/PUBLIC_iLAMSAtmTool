# core/chatbot/vector_store.py

from typing import List
import numpy as np
import faiss


class VectorStore:
    def __init__(self, embeddings: List[List[float]], chunks: List[str]):
        if len(embeddings) != len(chunks):
            raise ValueError("Embeddings and chunks length mismatch")

        self.chunks = chunks
        dim = len(embeddings[0])

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings).astype("float32"))

    def search(self, query_embedding: List[float], k: int = 5) -> List[str]:
        query_vector = np.array([query_embedding]).astype("float32")
        _, indices = self.index.search(query_vector, k)

        return [self.chunks[i] for i in indices[0]]
