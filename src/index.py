import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = "google/embeddinggemma-2"

def build_index(chunks, out_dir="index"):
    model = SentenceTransformer(MODEL_NAME, device="cuda")
    print("Model is on:", model.device)
    texts = [c["text"] for c in chunks]
    emb = model.encode(texts, prompt_name="Document",
                       batch_size=16, show_progress_bar=True,
                       normalize_embeddings=True)
    emb = np.asarray(emb, dtype="float32")

    index = faiss.IndexFlatIP(emb.shape[1])   # exact search, fine for thousands of chunks
    index.add(emb)

    import os; os.makedirs(out_dir, exist_ok=True)
    faiss.write_index(index, f"{out_dir}/chunks.index")
    with open(f"{out_dir}/chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)
    return index