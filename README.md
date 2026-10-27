# Course Material Search

Semantic search over lecture notes, slides, or past papers using EmbeddingGemma 2. Write a questions in your own words and gets most relevant notes or slides.

## Requirements
- Python 3.10-3.12
- Hugging Face account with access to 'google/embeddinggemma-2'
- (Optional) NVIDIA GPU: For more quick indexing, install Pytorch from https://pytorch.org first

## Setup
1. Clone the repo and open a terminal in the folder.
2. Create and activate a virtual enviroment:
    - Windows: 'python -m venv venv' then 'venv/Scripts/activate'
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

## Evaluation
See results in 'results' for the comparasion with a BM25 keyword baseline

## Limitation
- Scanned PDF and text inside image are not read.
- The index needs rebuilt fullt each time a document change is happend.
- Old '.doc' / '.ppt' format are not supported

.gitignore: make sure venv/, index/ , index_*/ ,data/raw, __pycache__/ and .env are listed. Don't commit lecturers materials.
