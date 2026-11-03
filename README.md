# Course Material Search

Semantic search over lecture notes, slides, or past papers using EmbeddingGemma 2. Write a questions in your own words and gets most relevant notes or slides.

## Requirements
- Python 3.10-3.12
- Hugging Face account with access to 'google/embeddinggemma-2'
- (Optional) NVIDIA GPU: For more quick indexing, install Pytorch from https://pytorch.org first 

## Setup
1. Clone the repo and open a terminal in the folder.
2. Create and activate a virtual enviroment:
    - Windows: 'python -m venv venv' then 'source venv/Scripts/activate'
    - Linux/Mac: 'python -m venv venv' then 'source venv/bin/activate
3. Install dependencies: 'pip install -r requirements.txt
4. Log in to the hugging face account: 'huggingface-cli login'
5. Put your PDF, DOCX OR PPTX files in data/raw
6. Build the index (takes a quite a while if you using the CPU): 'python main.py --rebuild'(first run donwload a model)
7. Start the app: 'streamlit run app.py

## Using the app
- Write a questions and press enter
- Add files from the sidebar, click **Save to library**, them **Rebuild index**

## Project structure
- course-search/
    - app/py                # Streamlit app (search, filter, RAG, upload)
    - main.py               # Command-line search/ index rebuild
    - README.md             # Setup and usage guide
    - requirement.txt       # dependency list
    - .gitignore
- src/                      # Core project(import by anything else)
    - __init__.py
    - extract.py            # Read the PDF/DOCX/PPTX
    - chunk.py              # Clean text is split into chunks
    - index.py              # Embed the chunks and build the FAISS index
    - search.py             # Searcher class
    - pipeline.py           # rebuild_index() and shared settings
    - rag.py                # Promt, call ollama, citation
    - evaluate.py           # BM25 baseline, Recall@k, MRR
- scripts/                  # one off tools (run from projects tools)
    - __init__.py 
    - run_eval.py           # BM25 vs EmbeddingGemma2
    - compare_chunks.py     # Chunk size expirement
    - run_rag_eval.py       # Generate a RAG answer for grading
    - calibrate.py          # Choose the MIN_SCORE to cutoff
    - test_rag.py           # Terminal RAG test
    - resize_background.py  # Shrink the background image
    - checks/
        - __init__.py
        - debug_eval.py     # Find the test-label mistmatches
        - check_test_set.py # Validate the test_set.json
        - compare_index.py  # Raw pages vs  what is indexed
- data/
    - raw/                  # all .pdf/.docx/.pptx 
    - test_set.json         # 50 questions evaluate
    - rag_test_set.json     # 30 RAG questions with reference answers
- results/                  # Evaluation output 
    - baseline.json
    - feedback.csv
    - rag_answers.csv
- assets/
    - background.jpg        # optional UI background
- docs/
    - setup_notes.md
    - indexed_files.txt


## Evaluation
See results in 'results' for the comparasion with a BM25 keyword baseline

## Limitation
- Scanned PDF and text inside image are not read.
- The index needs rebuilt fullt each time a document change is happend.
- Old '.doc' / '.ppt' format are not supported
- RAG needed gpu with atleast 6 gb VRAM

.gitignore: make sure venv/, index/ , index_*/ ,data/raw, __pycache__/ and .env are listed. Don't commit lecturers materials.
