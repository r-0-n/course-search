import json
from src.search import Searcher

tests =json.load(open("data/rag_test_set.json", encoding="utf-8"))
s = Searcher()

ans, unans = [], []
for t in tests:
    top = s.search(t["question"], k=1)[0]["score"]
    (ans if t["answerable"] else unans).append(top)

print("Answerable top scores:  ", [round(x, 2) for x in sorted(ans)])
print("Unanswerable top scores:", [round(x, 2) for x in sorted(unans)])

print("\nthreshold } answerable kept | uanswerable blocked")
for th in [x / 100 for x in range(20, 80, 5)]:
    kept = sum(a >= th for a in ans) / len(ans)
    blocked = sum(u < th for u in unans) / len(unans)
    print(f"  {th:.2f}    |         {kept:.0%}       |          {blocked:.0%}")