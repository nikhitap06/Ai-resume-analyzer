from dataclasses import dataclass, asdict
import re
import fitz

@dataclass
class Resume:
    filename: str
    pages: int
    text: str
    sections: dict
    contact: dict
    def to_dict(self): return asdict(self)

def _sections(text):
    labels = r"(?im)^(summary|objective|experience|work experience|education|projects?|skills?|certifications?|achievements?|awards?)\s*:?[ \t]*$"
    hits = list(re.finditer(labels, text))
    out = {}
    for i, m in enumerate(hits):
        key = m.group(1).lower().replace(' ', '_')
        end = hits[i+1].start() if i+1 < len(hits) else len(text)
        out[key] = text[m.end():end].strip()
    return out

def parse_resume(file_bytes, filename='resume.pdf'):
    try:
        doc = fitz.open(stream=file_bytes, filetype='pdf')
        text = '\n'.join(page.get_text('text') for page in doc).strip()
        if not text: raise ValueError('No selectable text found. This may be a scanned PDF; OCR is not enabled.')
        email = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        phone = re.search(r'(?:\+?\d[\d\s().-]{7,}\d)', text)
        first = next((x.strip() for x in text.splitlines() if x.strip()), 'Not detected')
        return Resume(filename, len(doc), text, _sections(text), {'name': first, 'email': email.group(0) if email else 'Not detected', 'phone': phone.group(0) if phone else 'Not detected'})
    except Exception as e:
        raise ValueError(f'Resume parsing failed: {e}') from e
