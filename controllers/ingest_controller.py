"""CONTROLLER: builds the vector database from the PDF. Run once.
It only gives orders: PDF -> chunks -> vectors -> database. The View shows progress."""

from collections import Counter
import config
from models import pdf_loader, chunker, embedder, vector_store
from views import terminal_view as view

BATCH = 32  # embed 32 chunks at a time

def run():
    view.show(f"Reading {config.PDF_FILE} ...")
    try:
        pages, total_pages = pdf_loader.read_pdf(config.PDF_FILE)
    except FileNotFoundError:
        view.show(f"PDF not found: {config.PDF_FILE}. Copy your Ramayana PDF there.")
        return

    view.show(
        f"Pages in PDF: {total_pages}   |   Pages with readable text: {len(pages)}"
    )
    if not pages:
        view.show(
            "No text found. Your PDF is probably scanned images. It needs OCR first."
        )
        return
    if len(pages) < total_pages * 0.5:
        view.show("WARNING: many pages have no text. They may be scanned images.")
    middle = pages[len(pages) // 2]
    view.show(
        f"\nSample text from page {middle['number']} (check it looks like normal text):"
    )
    view.show("   " + middle["text"][:300] + "...\n")

    chunks = chunker.make_chunks(pages, config.CHUNK_SIZE)
    view.show(f"Chunks created: {len(chunks)}")
    for kanda, count in Counter(c.kanda for c in chunks).items():
        view.show(f"   {count:5d}  {kanda}")
    if all(c.kanda == "Unknown" for c in chunks):
        view.show(
            "Note: no kanda headings found. Answers will cite page numbers only. That is fine."
        )

    vector_store.reset()
    for start in range(0, len(chunks), BATCH):
        batch = chunks[start : start + BATCH]
        vectors = embedder.embed_documents([c.text for c in batch])
        vector_store.save(batch, vectors)
        view.show(f"Saved {min(start + BATCH, len(chunks))} / {len(chunks)}")
    view.show("Done. The vector database is ready.")
