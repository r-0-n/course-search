from src.search import Searcher
from src.rag import answer

s = Searcher()
while True:
    q = input("\nQuestion (or 'quit')")
    if q.lower() == "quit":
        break
    r = answer(q, s)
    print("\nANSER:", r["answer"])
    print(f"(cited {r['cited']}, valid={r['valid_citation']}, {r['latency']}s)")
    for i, h in enumerate(r["hits"], start=1):
        print(f"  [{i}] {h['source']} ({h['location']}) sccore ={h['score']:.3f}")