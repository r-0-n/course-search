import json, os
from src.search import Searcher
from src.evaluate import BM25Searcher, evaluate

with open("index/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)
with open("data/test_set.json", encoding="utf-8") as f:
    test_set = json.load(f)

systems = {
    "BM25 (keyword)": BM25Searcher(chunks),
    "EmbeddingGemma 2": Searcher(),
}

os.makedirs("results", exist_ok=True)
all_results = {}
for name, searcher in systems.items():
    res = evaluate(searcher, test_set)
    all_results[name] = res
    print(f"\n=== {name} ===")
    print("Overall:", res["overall"])
    for t, m in res["by_type"].items():
        print(f"  {t}: {m}")

with open("results/baseline.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)
print("\nSaved to results/baseline.json")