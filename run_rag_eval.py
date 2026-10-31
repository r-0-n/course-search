import csv, json, os, time
import ollama 
from src.search import Searcher
from src.rag import answer, GEN_MODEL, GEN_OPTIONS
from src.evaluate import is_relevant

tests = json.load(open("data/rag_test_set.json", encoding="utf-8"))
searcher = Searcher()
os.makedirs("result", exist_ok=True)

def no_retrieval_answer(question):
    resp = ollama.chat(
        model=GEN_MODEL,
        messages=[{"role": "user",
                   "content": f"Answer briefly: {question}"}],
         options=GEN_OPTIONS,          
    )
    return resp["message"]["content"].strip()

rows = []
for t in tests:
    r = answer(t["question"], searcher)
    retreival_hit =""
    if  t["answerable"]:
        retrieval_hit = int(any(is_relevant(h , t) for h in r["hits"]))
    rows.append({
        "id": t["id"],
        "question": t["question"],
        "answerable": int(t["answerable"]),
        "reference": t["reference"],
        "top_score": round(r["hits"][0]["score"], 3) if r["hits"] else "",
        "retrieval_hit": retrieval_hit,
        "rag_answer": r["answer"],
        "cited": " ".join(map(str, r["cited"])),
        "valid_citations": int(r["valid_citations"]),
        "latency_s": r["latency"],
        "no_retrieval_answer": no_retrieval_answer(t["question"]),
        # fill with hand later :
        "correctness_0_1_2": "",
        "faithful_1_0": "",
        "citations_ok_1_0": "",
        "refusal_ok_1_0": "",
        "baseline_correctness_0_1_2": "",
        "notes": "",
    })
    print(f"{t['id']} done ({r['latency']}s)")
path = "results/rag_answers.csv"
with open(path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print("Saved", path)