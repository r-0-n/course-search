import os
from src.extract import extract_folder
from src.chunk import build_chunks
from src.index import build_index

RAW_DIR = "data/raw"
INDEX_DIR = "index"
SUPPORTED = [".pdf", ".docx", ".pptx"]

CHUNK_SIZE = 250
OVERLAP = 50
MIN_WORDS = 5

def index_exists():
    return (os.path.exists(f"{INDEX_DIR}/chunks.index")
            and os.path.exists(f"{INDEX_DIR}/chunks.json"))

def rebuild_index():
    """Re-read every file in data/raw and rebuild the index. Returns (number of pages/slides, number of chunks)"""
    records = extract_folder(RAW_DIR, supported=SUPPORTED)
    chunks = build_chunks(records, size=CHUNK_SIZE, overlap=OVERLAP,
                          min_words=MIN_WORDS)
    if not chunks:
        raise ValueError(
            "No text could be extracted. Check that data/raw contains"
            "text-based PDF, DOCX or PPTX files."
        )
    build_index(chunks, out_dir=INDEX_DIR)
    return len(records), len(chunks)


