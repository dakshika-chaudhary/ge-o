from pypdf import PdfReader
from typing import BinaryIO


def extract_text_from_pdf(uploaded_file: BinaryIO) -> str:
    """Extract text from an uploaded PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text)
        return "\n".join(pages).strip()
    except Exception as exc:
        raise RuntimeError(f"PDF text extraction failed: {exc}") from exc
