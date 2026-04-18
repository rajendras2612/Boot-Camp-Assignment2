from pathlib import Path
from typing import Iterable, List, Tuple

from PyPDF2 import PdfReader


def extract_text_blocks(pdf_path: Path) -> List[Tuple[str, int]]:
    """Extract text for each page with page information."""
    reader = PdfReader(pdf_path)
    blocks: List[Tuple[str, int]] = []
    for page_index, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            blocks.append((text.strip(), page_index + 1))
    return blocks


def extract_images(pdf_path: Path, output_dir: Path) -> List[Path]:
    """Save embedded images from a PDF and return the saved file paths."""
    # PyPDF2 doesn't easily extract images, so we'll return empty list for now
    # This is a simplified version - in production you'd want proper image extraction
    output_dir.mkdir(parents=True, exist_ok=True)
    return []


def chunk_text(text: str, chunk_size: int, overlap: int) -> Iterable[str]:
    """Create overlapping text chunks for retrieval."""
    if not text:
        return []

    cleaned = " ".join(text.split())
    words = cleaned.split(" ")
    chunks: List[str] = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += max(chunk_size - overlap, 1)
    return chunks


def block_to_documents(blocks: List[Tuple[str, int]], chunk_size: int, overlap: int) -> List[Tuple[str, dict]]:
    documents = []
    for page_text, page_number in blocks:
        for chunk in chunk_text(page_text, chunk_size, overlap):
            metadata = {
                "page": str(page_number),
                "source": "pdf_text",
                "text": chunk,
            }
            documents.append((chunk, metadata))
    return documents
