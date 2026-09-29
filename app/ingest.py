"""Extract text per page and split it into overlapping chunks."""
from pathlib import Path

CHUNK_WORDS = 150
OVERLAP_WORDS = 30


def extract_pages(filename: str, raw: bytes) -> list[str]:
    """Return a list of page texts. Non-PDF files are treated as one page."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(raw))
        return [page.extract_text() or "" for page in reader.pages]
    return [raw.decode("utf-8", errors="replace")]


def chunk_page(text: str) -> list[str]:
    """Split one page's text into overlapping word chunks."""
    words = text.split()
    if not words:
        return []
    chunks = []
    step = CHUNK_WORDS - OVERLAP_WORDS
    for start in range(0, len(words), step):
        piece = words[start:start + CHUNK_WORDS]
        if not piece:
            continue
        chunks.append(" ".join(piece))
        if start + CHUNK_WORDS >= len(words):
            break
    return chunks


def chunk_document(filename: str, raw: bytes) -> list[dict]:
    """Return chunk records: {source, page, text} for a whole document."""
    pages = extract_pages(filename, raw)
    records = []
    for page_num, page_text in enumerate(pages, start=1):
        for chunk_text in chunk_page(page_text):
            records.append({
                "source": filename,
                "page": page_num,
                "text": chunk_text,
            })
    return records
