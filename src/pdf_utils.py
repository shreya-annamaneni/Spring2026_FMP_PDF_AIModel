import re
import fitz


def load_pdf_from_path(pdf_path: str) -> bytes:
    with open(pdf_path, "rb") as f:
        return f.read()


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_pdf_pages(pdf_bytes: bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []

    for i, page in enumerate(doc):
        text = page.get_text("text") or ""
        text = clean_text(text)
        pages.append({
            "page_num": i + 1,
            "text": text
        })

    return pages