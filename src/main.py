from src.extract import extract_folder
from src.chunk import build_chunks
from src.index import build_index
from src.search import Searcher
import sys, os

if not os.path.exists("index/chunks.index") or "--rebuild" in sys.argv:
    records = extract_folder("data/raw")
    chunks = build_chunks(records)
    print(f"{len(records)} pages/slides → {len(chunks)} chunks")
    build_index(chunks)

s = Searcher()
while True:
    q = input("\nQuestion (or 'quit'): ")
    if q.lower() == "quit":
        break
    for r in s.search(q):
        print(f"[{r['score']:.3f}] {r['source']} ({r['location']})")
        print("   ", r["text"][:200], "...\n")

