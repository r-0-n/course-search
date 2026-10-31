import gc
import csv, os, re, time
import base64
from pathlib import Path
from datetime import datetime
from collections import Counter
from pathlib import Path
from src.rag import stream_answer, is_answerable, NOT_FOUND, TOP_K
from src.rag import MIN_SCORE

import streamlit as st

from src.search import Searcher
from src.pipeline import rebuild_index, index_exists, RAW_DIR, SUPPORTED

st.set_page_config(page_title="Course Materials Search",
                   page_icon="🔎", layout="wide")

@st.cache_data
def load_b64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()

SIDEBAR_LIGHT = "224,236,255"
SIDEBAR_DARK = "224,236,255"
SIDEBAR_ALPHA = 0.85

def is_dark():
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return False

def set_background(path, overlay=0.85):
    dark = is_dark()
    base = "14,17,23" if dark else "255,255,255"
    panel = "38,39,48" if dark else "255,255,255"
    side = SIDEBAR_DARK if dark else SIDEBAR_LIGHT  
    ext = Path(path).suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext     # png, webp
    b64 = load_b64(str(path))
    st.markdown(f"""
    <style>
    .stApp {{
        background-image:
            linear-gradient(rgba(255,255,255,{overlay}), rgba(255,255,255,{overlay})),
            url("data:image/{mime};base64,{b64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{
        background: transparent;
    }}
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {{
        background: rgba(255,255,255,0.70);
        backdrop-filter: blur(6px);
    }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(255,255,255,0.65);
        border-radius: 12px;
    }}
    </style>
    """, unsafe_allow_html=True)


BG = Path("assets/background.jpg")
if BG.exists():
    set_background(BG, overlay=0.85)

@st.cache_resource(show_spinner="Loading model and index...")
def load_searcher():
    return Searcher()

def free_memory():
    """Release the loaded model before rebuildingm so two copies
    don't sit in GPU/RAM at once."""
    st.cache_resource.clear()
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass    



#----------------------------- Sidebar: Library and Upload -----------------------------
with st.sidebar:
    st.header("Document library")

    if index_exists():
        searcher = load_searcher()
        counts = Counter(c["source"] for c in searcher.chunks)
        st.success(f"{len(counts)} files ' {len(searcher.chunks)} chunks indexed")
        with st.expander("Show indexed files"):
            for name, n in sorted(counts.items()):
                st.write(f"• {name} ({n} chunks)")

    else:
        searhcer = None
        st.warning("Non index yet, Upload documents and build the index")


    st.divider()
    st.subheader("Add documents")
    uploaded = st.file_uploader(
        "PDF, Word or PowerPoint files",
        type=[ext.lstrip(".") for ext in SUPPORTED],
        accept_multiple_files=True,
    )

    if st.button("Save to library", disabled=not uploaded):
        Path(RAW_DIR).mkdir(parents=True, exist_ok=True)
        saved, skipped = [],[]
        for f in uploaded:
            name = Path(f.name).name
            dest = Path(RAW_DIR) / name
            if dest.exists():
                skipped.append(name)
            else:
                dest.write_bytes(f.getbuffer())
                saved.append(name)
        if saved:
            st.session_state["Needs rebuild"] = True
            st.success(f"Saved {len(saved)} file(s).")
        if skipped:
            st.info("Already in library, skipped: "+ ",".join(skipped))

    if st.session_state.get("needs_rebuild") or not index_exists():
        st.warning("The index is out of date. Rebuild to Include new file.")

    if st.button("Rebuild index"):
        free_memory()
        try:
            with st.spinner("Reading documents and building index. "
                            "This can take a few minutes..."):
                pages, chunks = rebuild_index()
            st.session_state["needs_rebuild"] = False
            st.success(f"Done: {pages} pages/slides → {chunks} chunks.")
            st.rerun()
        except Exception as e:
            st.error(f"Could not build the index: {e}")

# ---------------- Sidebar filters ----------------
if searcher is None:
    st.title("🔎 Course Materials Search")
    st.info("Add documents in the sidebar, then click **Rebuild index**.")
    st.stop()

with st.sidebar:
    st.divider()
    st.subheader("Filters")
    hide_papers = st.checkbox("Hide past tests and quizzes")
    all_files = sorted({c["source"] for c in searcher.chunks})
    chosen = st.multiselect("Only search these files", all_files)

# ---------------- Helpers ----------------
EXAMPLES = [
    "what does a firewall do?",
    "how do I make a web page fit different screen sizes?",
    "difference between symmetric and asymmetric encryption",
]
PAPER_WORDS = ("test", "quiz", "tutorial", "exam")   # adjust to your file names


def is_paper(name):
    return any(w in name.lower() for w in PAPER_WORDS)


def relevance(score):
    # Calibrate these cut-offs from your own score data
    if score >= 0.60:
        return "Strong match"
    if score >= 0.45:
        return "Good match"
    return "Possible match"


def highlight(text, query):
    text = text.replace("$", r"\$")      # stops "$" in accounting notes becoming maths
    words = [w for w in re.findall(r"\w+", query) if len(w) > 3]
    if not words:
        return text
    pattern = re.compile("(" + "|".join(map(re.escape, words)) + ")", re.IGNORECASE)
    return pattern.sub(r"**\1**", text)


def log_feedback(label, query, hit, rank):
    os.makedirs("results", exist_ok=True)
    path = "results/feedback.csv"
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "query", "label", "rank", "source", "location", "score"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), query, label,
                    rank, hit["source"], hit["location"], round(hit["score"], 3)])
    st.toast("Thanks for the feedback!")


def use_example(text):
    st.session_state["q"] = text
    st.session_state["auto_run"] = True

# ---------------- Search form ----------------
st.title("🔎 Course Materials Search")
st.caption("Ask a question in your own words. Results are ranked by meaning, "
           "not just matching keywords.")

with st.form("search_form", border=False):
    c1, c2 = st.columns([5, 1])
    c1.text_input("Your question", key="q",
                  placeholder="e.g. how do I stop the same data being stored twice?")
    k = c2.number_input("Results", min_value=1, max_value=15, value=5)
    use_rag = st.toggle("Also write a short answer from the top results (RAG)")
    submitted = st.form_submit_button("Search", type="primary")

run = submitted or st.session_state.pop("auto_run", False)
query = st.session_state.get("q", "").strip()

if run and query:

    t0 = time.time()
    with st.spinner("Searching..."):
        st.session_state["hits"] = searcher.search(query, k=30)   # fetch extra, filter later
    st.session_state["search_time"] = time.time() - t0
    st.session_state["last_query"] = query

# ---------------- Empty state ----------------
if not st.session_state.get("hits"):
    st.markdown("**Try one of these:**")
    for i, ex in enumerate(EXAMPLES):
        st.button(ex, key=f"ex_{i}", on_click=use_example, args=(ex,))
    st.stop()

# ---------------- Results ----------------
def show_sources(hits, q):
    for rank, h in enumerate(hits, start=1):
        with st.container(border=True):
            st.markdown(f"**{rank}. {h['source']}**")
            st.caption(f"{h['location']} . {relevance(h['score'])} ({h['score']:.2f})")
            snippet = h["text"][:300] + ("..." if len(h["text"]) > 300 else "")
            st.markdown(highlight(snippet, q))
            if len(h["text"]) > 300:
                with st.expander("Show full passage"):
                    st.write(h["text"])
            b1, b2, _= st.columns([1, 1, 8])
            b1.button("👍", key=f"up_{rank}", help="Helpful",
                      on_click=log_feedback, args=("helpful", q, h, rank))
            b2.button("👎", key=f"down_{rank}", help="Not helpful",
                      on_click=log_feedback, args=("not helpful", q, h, rank))

q = st.session_state["last_query"]
hits = [h for h in st.session_state["hits"]
        if (not hide_papers or not is_paper(h["source"]))
        and (not chosen or h["source"] in chosen)][:int(k)]

st.caption(f"{len(hits)} results for “{q}” in "
           f"{st.session_state['search_time']:.2f} s")

if not hits:
    st.warning("No results with these filters. Try removing a filter.")
    st.stop()

if hits[0]["score"] < MIN_SCORE:
    st.warning("I couldn't find a good match for this question in your course "
               "materials. Try rephrasing it, or add the relevant document.")
    with st.expander("Show the closest results anyway"):
        show_sources(hits[:3], q)
    st.stop()

if use_rag:
    st.subheader("Answer")
    top = hits[:TOP_K]
    key = (q, tuple((h["source"], h["location"]) for h in top))
    if not is_answerable(top):
        st.warning(NOT_FOUND)
    elif st.session_state.get("answer_key") == key:
        st.write(st.session_state["answer"])
    else:
        try:
            st.session_state["answer"] = st.write_stream(stream_answer(q, top))
            st.session_state["answer_key"] = key
        except Exception as e:
            st.error(f"Could not reach the language model. Is Ollama running? ({e})")
        st.caption(f"Based on result 1 to {len(top)} below. Check the source before relying on it")

st.subheader("Sources")
show_sources(hits, q)

