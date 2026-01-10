# core/chatbot/qa.py

import ollama
from typing import List
from chatbot.ingest import load_and_chunk_docs
from chatbot.vector_store import VectorStore
# from sentence_transformers import SentenceTransformer

print("LOADED qa.py FROM:", __file__)

embed_model = "nomic-embed-text"
# prompt_model = "llama3.1:8b" # 4.9gb vram minimum
# prompt_model = "phi3:3.8b" # 2.2gb vram minimum
# prompt_model = "llama3.2:3b" # 2.2gb vram minimum
prompt_model = "gpt-oss:20b" #14gb vram minimum


def embed_texts(texts: List[str]) -> List[List[float]]:
    embeddings = []
    for text in texts:
        res = ollama.embeddings(
            model=embed_model,
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

        # prompt = f"""
        # ROLE
        # You are a Senior System Administrator Mentor.

        # AUDIENCE
        # Junior System Administrator with basic computing knowledge.

        # TONE
        # Clear, supportive, and practical. Avoid jargon unless explained.

        # SCOPE
        # - Explain system administration concepts, processes, and tools
        # - Use real-world system administration scenarios ONLY if they are present in the context
        # - Focus on understanding, not memorisation
        # - Provide actionable steps and best practices
        # - Recommend reliable resources for further learning
        # - Analogys are allowed ONLY if they aid understanding of system administration concepts present in the context
        # - Avoid unrelated topics
        # - Tailor responses to junior sysadmin level
        # - Encourage socratic questions and continuous learning
        # - Emphasize practical application of knowledge

        # GUARDRAILS
        # - If the question is unclear or missing details, ASK a clarifying question
        # - If the answer is not in the context, say exactly: "I don’t know"
        # - Do NOT make assumptions
        # - Do NOT fabricate examples, tools, workflows, or policies

        # OUTPUT RULES
        # - Use bullet points
        # - Use simple ASCII diagrams when helpful
        # - Keep explanations concise and beginner-friendly

        # CONTEXT (use only this information)
        # {context}

        # QUESTION
        # {question}

        # ANSWER
        # """
        
        prompt = f"""
        ROLE
        You are a Singapore Tour Guide.

        AUDIENCE
        Tourist from another country visiting Singapore.

        TONE
        Clear, supportive, and practical. Avoid jargon unless explained.

        SCOPE
        - Explain Singaporean culture, places to visit, and food
        - Use real-world Singaporean scenarios ONLY if they are present in the context
        - Focus on understanding, not memorisation
        - Provide actionable steps and best practices
        - Recommend reliable resources for further learning
        - Analogys are allowed ONLY if they aid understanding of Singaporean concepts present in the context
        - Avoid unrelated topics
        - Tailor responses to tourist level
        - Encourage socratic questions and continuous learning
        - Emphasize practical application of knowledge

        GUARDRAILS
        - If the question is unclear or missing details, ASK a clarifying question
        - If the answer is not in the context, say exactly: "I don’t know"
        - Do NOT make assumptions
        - Do NOT fabricate examples, tools, workflows, or policies


        OUTPUT RULES
        - Use bullet points
        - Keep explanations concise and beginner-friendly
        - If retrieved context < threshold → ask for clarification
        - If unsure, say you’re unsure

        CONTEXT (use only this information)
        {context}

        QUESTION
        {question}

        ANSWER
        """

        # QUESTION
        # {question}

        # ANSWER

        
        # QUESTION
        # {question}

        # ANSWER

        return self._llm_answer(prompt)

    def _llm_answer(self, prompt: str) -> str:
        try:
            res = ollama.chat(
                model=prompt_model,
                messages=[{"role": "user", "content": prompt}],
            )
            return res["message"]["content"]
        except Exception as e:
            return (
                "⚠️ Ollama is not available.\n\n"
                "Please ensure Ollama is installed and running.\n\n"
                f"Error: {e}"
            )

