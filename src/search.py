import json, numpy as np, faiss
from sentence_transformers import SentenceTransformer

class Searcher:
    def __init__(self, index_dir="index", model_name="google/embeddinggemma-2"):
        self.model = SentenceTransformer(model_name, device="cuda")
        self.index = faiss.read_index(f"{index_dir}/chunks.index")
        with open(f"{index_dir}/chunks.json", encoding="utf-8") as f:
            self.chunks = json.load(f)

    def search(self, query, k=5):
        q = self.model.encode(query, prompt_name="SearchQuery",
                              normalize_embeddings=True)
        scores, ids = self.index.search(np.asarray([q], dtype="float32"), k)
        return [{**self.chunks[i], "score": float(s)}
                for s, i in zip(scores[0], ids[0])]