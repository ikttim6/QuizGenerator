import fitz  # PyMuPDF
import os

def extract_text_from_file(file_path):
    abs_path = os.path.abspath(file_path)
    text = ""
    with fitz.open(abs_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

