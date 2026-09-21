"""
Split cleaned text into overlapping chunks.

Why chunks?
- Embedding models have a max length (~256 tokens for MiniLM)
- Smaller chunks = more precise retrieval
- Overlap preserves context across chunk boundaries
"""

from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    chunk_index: int


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[Chunk]:
    """
    Split text into overlapping chunks by character count.
    Tries to break on sentence boundaries when possible.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be > overlap")

    chunks = []
    start = 0
    index = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Try to end on a sentence boundary
        if end < text_len:
            for boundary in [". ", "! ", "? ", "\n"]:
                last_boundary = text.rfind(boundary, start, end)
                if last_boundary > start + (chunk_size // 2):
                    end = last_boundary + len(boundary)
                    break

        chunk_str = text[start:end].strip()
        if chunk_str:
            chunks.append(Chunk(text=chunk_str, chunk_index=index))
            index += 1

        start = end - overlap
        if start <= 0 or end >= text_len:
            break

    return chunks


def chunk_document(text: str, chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Wrapper with logging."""
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    print(f"  Created {len(chunks)} chunks")
    avg = sum(len(c.text) for c in chunks) // max(len(chunks), 1)
    print(f"  Avg chunk size: {avg} chars")
    return chunks
