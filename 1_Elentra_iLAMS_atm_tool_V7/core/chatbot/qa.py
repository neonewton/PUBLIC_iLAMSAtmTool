# core/chatbot/qa.py

import ollama
from typing import List

from core.chatbot.ingest import load_and_chunk_docs
from core.chatbot.vector_store import VectorStore

print("LOADED qa.py FROM:", __file__)

def embed_texts(texts: List[str]) -> List[List[float]]:
    embeddings = []
    for text in texts:
        res = ollama.embeddings(
            model="nomic-embed-text",
            prompt=text
        )
        embeddings.append(res["embedding"])
    return embeddings


class KnowledgeAssistant:
    def __init__(self):
        # 1️⃣ Load knowledge
        self.chunks = load_and_chunk_docs()

        # 2️⃣ Embed knowledge (Ollama)
        self.embeddings = embed_texts(self.chunks)

        # 3️⃣ Build vector store
        self.vector_store = VectorStore(self.embeddings, self.chunks)

    def retrieve_context(self, question: str, k: int = 5) -> List[str]:
        query_embedding = embed_texts([question])[0]
        return self.vector_store.search(query_embedding, k=k)

    def answer(self, question: str) -> str:
        context_chunks = self.retrieve_context(question)
        context = "\n\n".join(context_chunks)

        prompt = f"""
            You are an assistant specialised in internal documentation.
            Answer ONLY using the context below.
            If the answer is not found, reply exactly: "I don’t know."

            Context:
            {context}

            Question:
            {question}
        """

        return self._llm_answer(prompt)

    def _llm_answer(self, prompt: str) -> str:
        res = ollama.chat(
            model="llama3.1",
            messages=[{"role": "user", "content": prompt}],
        )
        return res["message"]["content"]
