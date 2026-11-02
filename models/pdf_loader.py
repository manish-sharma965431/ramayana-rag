"""MODEL: reads the PDF and gives back the text of every page."""

import re
from pypdf import PdfReader

# Words used to spot a heading such as "Aranya Kanda" on a page
KANDA_PATTERN = re.compile(
    r"(bala|ayodhya|aranya|kishkindha|kishkinda|sundara|yuddha|lanka|uttara)\s*kaa?nda?",
    re.IGNORECASE,
)


def split_heading(raw_text):
    """Find a kanda heading line (a SHORT line like 'Aranya Kanda').
    Returns (heading or None, the page text without the heading line).
    We remove the heading so a running page header does not repeat inside every chunk."""
    heading = None
    kept_lines = []
    for line in raw_text.splitlines():
        if len(line.strip()) <= 60 and KANDA_PATTERN.search(line):
            heading = line.strip()
        else:
            kept_lines.append(line)
    return heading, "\n".join(kept_lines)


def clean(raw_text):
    """Join words split by a hyphen at the end of a line, and remove extra spaces/newlines."""
    text = raw_text.replace("-\n", "")
    return " ".join(text.split())


def read_pdf(path):
    """Returns (pages, total_pages). Each page is {"number", "kanda", "text"}."""
    reader = PdfReader(path)
    pages = []
    current_kanda = "Unknown"
    for number, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        heading, body = split_heading(raw_text)
        if heading:
            current_kanda = heading
        text = clean(body)
        if text:  # skip empty pages
            pages.append({"number": number, "kanda": current_kanda, "text": text})
    return pages, len(reader.pages)
