import re

def clean(text):
    text = re.sub(r"\s+"," ". text)
    return text.strip()


def chunk_text(text, size=250, overlap=50):
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        chunks.append(" ".join(words[start:start + size]))
        start += size - overlap
    return chunks

def build_chunks(records, size=250, overlap=50, min_words=15):
    chunks = []
    for r in records:
        text = clean(r["text"])
        if len(text.split()) < min_words:   # skip near-empty pages/slides
            continue
        for j, piece in enumerate(chunk_text(text, size, overlap)):
            chunks.append({
                "id": len(chunks),
                "source": r["source"],
                "location": r["location"],
                "text": piece,
            })
    return chunks
