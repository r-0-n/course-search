import json
from src.extract import extract_folder
from src.chunk import build_chunks
from src.index import build_index
from src.search import Searcher
from src.evaluate import BM25Searcher , evaluate

with open("data/test_set.json", encoding="utf-8") as f:
    test_set = json.load(f)

records = extract_folder("data/raw")
configs = [(150, 30), (250, 50), (400, 80)]
summary = {}

for size, overlap in configs:
    chunks = build_chunks(records, size=size, overlap=overlap)
    out_dir = f"index_{size}"
    build_index(chunks, out_dir=out_dir)

    emb = evaluate(Searcher(index_dir=out_dir), test_set)["overall"]
    bm = evaluate(BM25Searcher(chunks), test_set)["overall"]
    summary[f"size={size}, overlap={overlap}"] = {
        "chunks": len(chunks), "embeddings": emb, "bm25": bm,
    }
    print(f"\nsize={size}: {len(chunks)} chunks")
    print(" embeddings:", emb)
    print(" bm25:      ", bm)

with open("result/chunk_sizes.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

