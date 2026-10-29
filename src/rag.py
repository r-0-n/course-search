import re
import time
import ollama

GEN_MODEL = "YOUR_MODEL_TAG"      # the tag shown by `ollama list`
TOP_K = 4                         # chunks sent to the model
MIN_SCORE = 0.30                  # tune this from your own data (see Step 4)
MAX_CHARS = 1800                  # cap per chunk to keep the prompt short
GEN_OPTIONS = {"temperature": 0, "num_ctx": 4096}

NOT_FOUND = "I could not find this in the course materials."

SYSTEM_PROMPT = f"""You are a study assistant answering questions about course materials.
Rules:
1. Use ONLY the numbered context passages provided. Do not use outside knowledge.
2. If the passages do not contain the answer, reply exactly: {NOT_FOUND}
3. Keep the answer short (2 to 5 sentences) and clear for a student.
4. After each claim, cite the passage number in square brackets, like [1] or [2][3].
5. Never invent page numbers, file names or facts."""


def build_context(hits):
    parts = []
    for i, h in enumerate(hits, start=1):
        text = h["text"][:MAX_CHARS]
        parts.append(f"[{i}] ({h['source']}, {h['location']})\n{text}")
    return "\n\n".join(parts)


def build_messages(question, hits):
    user = f"Context passages:\n\n{build_context(hits)}\n\nQuestion: {question}\n\nAnswer:"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def is_answerable(hits):
    """Skip generation when even the best match is weak."""
    return bool(hits) and hits[0]["score"] >= MIN_SCORE


def stream_answer(question, hits, model=GEN_MODEL):
    """Yields text pieces as they are generated (for the Streamlit app)."""
    for chunk in ollama.chat(model=model,
                             messages=build_messages(question, hits),
                             stream=True, options=GEN_OPTIONS):
        yield chunk["message"]["content"]


def generate(question, hits, model=GEN_MODEL):
    resp = ollama.chat(model=model,
                       messages=build_messages(question, hits),
                       options=GEN_OPTIONS)
    return resp["message"]["content"].strip()


def cited_numbers(answer):
    return sorted({int(n) for n in re.findall(r"\[(\d+)\]", answer)})


def answer(question, searcher, k=TOP_K, model=GEN_MODEL):
    """Full RAG call for scripts and evaluation."""
    start = time.time()
    hits = searcher.search(question, k=k)
    if not is_answerable(hits):
        text = NOT_FOUND
    else:
        text = generate(question, hits, model=model)
    cited = cited_numbers(text)
    return {
        "answer": text,
        "hits": hits,
        "cited": cited,
        "valid_citations": all(1 <= n <= len(hits) for n in cited),
        "latency": round(time.time() - start, 1),
    }