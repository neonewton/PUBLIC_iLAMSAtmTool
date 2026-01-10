# core/chatbot/ingest.py

from pathlib import Path
from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    chunks = []
    step = chunk_size - overlap

    for i in range(0, len(text), step):
        chunk = text[i:i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)

    return chunks


def load_and_chunk_docs(knowledge_dir: str = "knowledge_base") -> List[str]:
    all_chunks: List[str] = []

    base_path = Path(knowledge_dir)
    if not base_path.exists():
        raise FileNotFoundError(f"Knowledge directory not found: {knowledge_dir}")

    for file in base_path.glob("*.md"):
        text = file.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        all_chunks.extend(chunks)

    if not all_chunks:
        raise ValueError("No knowledge chunks were generated.")

    return all_chunks
