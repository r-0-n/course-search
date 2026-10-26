import sys, json
from src.extract import extract_folder

name= sys.argv[1]
chunks = json.load(open("index/chunks.json", encoding="utf-8"))
in_index = { c["location"] for c in chunks if c["source"] == name }

for r in extract_folder("data/raw"):
    if r["source"] == name:
        n = len(r["text"].split())
        status = "in index" if r["location"] in in_index else "Missing from index"
        print(f'{r["location"]:>10} {n:>4} words{status}')