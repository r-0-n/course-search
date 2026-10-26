import sys
from src.extract import extract_folder

name = sys.argv[1]
for r in extract_folder("data/raw"):
    if r["source"] == name:
        print(r["location"], "-", len(r["text"].split()), "words")