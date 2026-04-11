import PyPDF2
import docx

def extract_text(path):
    text = ""

    if path.endswith(".pdf"):
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""

    elif path.endswith(".docx"):
        doc = docx.Document(path)
        for para in doc.paragraphs:
            text += para.text

    return text.lower()