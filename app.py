import gc
from collections import Counter
from pathlib import Path

import streamlit as st

from src.search import Searcher
from src.pipeline import rebuild_index, index_exists, RAW_DIR, SUPPORTED

st.set_page_config(page_title="Course Materials Search",
                   page_icon="🔎", layout="wide")

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
        Path(RAW_DIR).mkdir(parent=True, exist_ok=True)
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

#______________________ Main area: Search ______________________________________
st.title("Course Materials Search")
st.caption("Ask a question in your own words. Results are ranked by meaning,"
           "not just matching keywords.")

if searcher is None:
    st.info("Add documents in the sidebarm then click **Rebuild Index**.")
    st.stop

col1, col2 = st.columns([5,1])
query = col1.text_input("Your questions",
                        placeholder="e.g. how do I stop the same being stored twice?")
k = col2.number_input("Results", min_value=1, max_value=15, value=5)

if query.strip():
    with st.spinner("Searching..."):
        hits = searcher.search(query.strip(), k=int(k))

    st.subheader(f"Top {len(hits)} results")
    for rank, h in enumerate(hits, start=1):
        with st.container(border=True):
            st.markdown(f"**{rank}. {h['source']}**")
            st.caption(f"{h['location']} . similarity score {h['score']:.3f}")
            snippet = h ["text"][:300] + ("..." if len(h["text"]) > 300 else "")
            st.write(snippet)
            if len(h["text"]) > 300:
                with st.expander("Show full passage"):
                    st.write(h["text"])

