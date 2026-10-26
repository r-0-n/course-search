import re
from collections import defaultdict
from rank_bm25 import BM25Okapi


def tokenize(text):
    return re.findall(r"\w+", text.lower())


class BM25Searcher:
    """Keyword baseline over the same chunks as the embedding index."""
    def __init__(self, chunks):
        self.chunks = chunks
        self.bm25 = BM25Okapi([tokenize(c["text"]) for c in chunks])

    def search(self, query, k=5):
        scores = self.bm25.get_scores(tokenize(query))
        top = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
        return [{**self.chunks[i], "score": float(scores[i])} for i in top]


def norm(s):
    return s.strip().lower()

def is_relevant(hit, item):
    if hit["source"] != item["source"]:
        return False
    locs = item.get("locations") or []
    return (not locs) or (hit["location"] in locs)

def evaluate(searcher, test_set, ks=(1, 3, 5), mrr_depth=10):
    depth = max(max(ks), mrr_depth)
    overall = {"n": 0, "mrr": 0.0, **{f"recall@{k}": 0 for k in ks}}
    by_type = defaultdict(lambda: {"n": 0, "mrr": 0.0, **{f"recall@{k}": 0 for k in ks}})
    failures = []

    for item in test_set:
        results = searcher.search(item["question"], k=depth)
        rank = next((r for r, h in enumerate(results, start=1)
                     if is_relevant(h, item)), None)

        for bucket in (overall, by_type[item.get("type", "unknown")]):
            bucket["n"] += 1
            if rank:
                bucket["mrr"] += 1 / rank
                for k in ks:
                    if rank <= k:
                        bucket[f"recall@{k}"] += 1

        if rank is None or rank > max(ks):
            failures.append({
                "id": item["id"],
                "question": item["question"],
                "type": item.get("type"),
                "expected": f'{item["source"]} {item.get("locations")}',
                "rank": rank,
                "top_result": f'{results[0]["source"]} ({results[0]["location"]})',
            })

    def finish(b):
        n = b["n"]
        out = {"n": n, "MRR": round(b["mrr"] / n, 3)}
        for k in ks:
            out[f"Recall@{k}"] = round(b[f"recall@{k}"] / n, 3)
        return out

    return {
        "overall": finish(overall),
        "by_type": {t: finish(b) for t, b in by_type.items()},
        "failures": failures,
    }