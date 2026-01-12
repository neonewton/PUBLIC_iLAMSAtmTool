# core/chatbot/ingest.py

from pathlib import Path
from typing import List
from docling.document_converter import DocumentConverter
from pdf2image import convert_from_path
import pytesseract


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    chunks = []
    step = chunk_size - overlap

    for i in range(0, len(text), step):
        chunk = text[i : i + chunk_size].strip()
        if len(chunk) > 200:
            chunks.append(chunk)

    return chunks

def ocr_pdf(file_path: Path) -> str:

    images = convert_from_path(file_path)
    text = "\n".join(pytesseract.image_to_string(img) for img in images)
    return text.strip()


def parse_with_docling(file_path: Path) -> str:
    converter = DocumentConverter()
    result = converter.convert(str(file_path))

    try:
        text = result.document.export_to_markdown()
        source = "markdown"
    except Exception:
        text = result.document.export_to_text()
        source = "text"

    text = text.strip()

    print(f"[Docling] {file_path.name} | method={source} | chars={len(text)}")

    if len(text) < 300 and file_path.suffix == ".pdf":
        print(f"[WARN] Very little text extracted from {file_path.name}")
        text = ocr_pdf(file_path)

    return text



def load_and_chunk_docs() -> List[str]:
    """
    Load documents from knowledge_base/, parse them,
    chunk the text, and return all chunks.

    This function is intended to run ONCE per app lifecycle
    (cached by Streamlit).
    """

    # Resolve project root reliably:
    # ingest.py → core/chatbot → core → project root
    project_root = Path(__file__).resolve().parent.parent
    knowledge_dir = project_root / "knowledge_base"

    if not knowledge_dir.exists():
        raise FileNotFoundError(f"Knowledge directory not found: {knowledge_dir}")

    all_chunks: List[str] = []

    for file in sorted(knowledge_dir.iterdir()):
        suffix = file.suffix.lower()

        # --- Use Docling for rich documents ---
        if suffix in {".pdf", ".docx", ".pptx", ".html"}:
            raw_text = parse_with_docling(file)

        # --- Markdown / plain text ---
        elif suffix in {".md", ".txt"}:
            raw_text = file.read_text(encoding="utf-8")

        else:
            continue  # skip unsupported files

        chunks = chunk_text(raw_text)
        all_chunks.extend(chunks)

    if not all_chunks:
        raise ValueError("No knowledge chunks were generated.")

    return all_chunks

