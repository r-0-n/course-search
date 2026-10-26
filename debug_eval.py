import json
from src.search import Searcher

chunks = json.load(open("index/chunks.json", encoding="utf-8"))
tests = json.load(open("data/test_set.json", encoding="utf-8"))

index_sources ={c["source"] for c in chunks}
index_pairs = {(c["source"], c["location"]) for c in chunks}

print("Sources in index:", sorted(index_sources), "\n")

bad_source, bad_loc = 0,0
for t in tests:
    if t["source"] not in index_sources:
        bad_source += 1
        print(f"[Q{t['id']}] source NOT in index: {t['source']!r}")
    else:
        for loc in t.get("locations") or []:
            if (t["source"], loc) not in index_pairs:
                if (t["source"], loc) not in index_pairs:
                    bad_loc += 1
                    print(f"[Q{t['id']}] location NOT in index: {t['source']!r} / {loc!r}")
print(f"\nQuestions with a wrong source: {bad_source}")
print(f"Labels with a wrong location:{bad_loc}" )
