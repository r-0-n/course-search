from pathlib import Path
from pypdf import PdfReader
from docx import Document
from pptx import Presentation

def read_pdf(path):
    reader = PdfReader(path)
    return [(f"page{i}", page.extract_text() or "")
            for i, page in enumerate(reader.pages, start=1)]

def read_docx(path):
    doc = Document(path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [{"full document", text}]

def read_pptx(path):
    prs = Presentation(path)
    out = []
    for i, slide in enumerate(prs.slides, start=1):
        parts = [s.text_frame.text for s in slide .shapes if s.has_text_frame]
        if slide.has_notes_slide:
            parts.append(slide.notes_slide.notes_text_frame.text)
        out.append((f"slide {i}", "\n".join(parts)))
    return out
READERS = {".pdf": read_pdf, ".docx": read_docx, ".pptx": read_pptx}

def extract_folder(folder="data/raw"):
    records = []
    for path in sorted(Path(folder.rglob)("*")):
        reader = READERS.get(path.suffix.lower())
        if reader:
            for location, text in reader(path):
                records.append({"source": path.name, "location": location, "text": text})
    return records