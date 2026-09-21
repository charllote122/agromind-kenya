"""
PDF text extraction and cleaning.

Real PDFs are messy. This module:
1. Extracts raw text from a PDF
2. Removes repeating headers/footers
3. Removes page numbers
4. Fixes broken hyphenation
5. Normalizes whitespace
"""

import re
from pathlib import Path
from collections import Counter
from pypdf import PdfReader


def extract_raw_text(pdf_path: str) -> str:
    """Extract raw text from all pages of a PDF."""
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n\n".join(pages)


def find_repeating_lines(text: str, min_repeats: int = 3) -> set:
    """
    Find lines that repeat across pages (headers/footers).
    A line appearing 3+ times is almost certainly a header/footer.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    counts = Counter(lines)
    return {line for line, count in counts.items() if count >= min_repeats}


def clean_text(raw_text: str) -> str:
    """Apply cleaning steps to raw PDF text."""
    text = raw_text

    # 1. Remove repeating header/footer lines
    repeating = find_repeating_lines(text, min_repeats=3)
    lines = text.split("\n")
    lines = [line for line in lines if line.strip() not in repeating]
    text = "\n".join(lines)

    # 2. Remove standalone page numbers
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # 3. Fix hyphenation across line breaks: "agricul-\nture" -> "agriculture"
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    # 4. Collapse multiple newlines
    text = re.sub(r"\n{2,}", "\n", text)

    # 5. Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    # 6. Strip each line, drop empty ones
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    text = "\n".join(lines)

    return text


def load_and_clean(pdf_path: str) -> str:
    """Full pipeline: extract + clean."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    raw = extract_raw_text(pdf_path)
    cleaned = clean_text(raw)

    print(f"  Raw text length:     {len(raw):,} characters")
    print(f"  Cleaned text length: {len(cleaned):,} characters")
    reduction = (1 - len(cleaned) / max(len(raw), 1)) * 100
    print(f"  Reduction:           {reduction:.1f}%")

    return cleaned
