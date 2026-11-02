"""MODEL: cuts the book text into small pieces (chunks) so we can search them."""

import re
from dataclasses import dataclass

@dataclass
class Chunk:
    id: str
    text: str
    page: int
    kanda: str


def split_sentences(text):
    """Cut text into sentences at . ! ?"""
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s]


def cut_long_sentence(sentence, max_chars):
    """Some PDF text has no full stops. Cut such a long 'sentence' at word boundaries."""
    pieces, current = [], ""
    for word in sentence.split():
        if len(current) + len(word) + 1 > max_chars and current:
            pieces.append(current)
            current = ""
        current = (current + " " + word).strip()
    if current:
        pieces.append(current)
    return pieces


def make_chunks(pages, max_chars):
    # Step 1: make one list of sentences, each remembering its page and kanda
    sentences = []
    for page in pages:
        for sentence in split_sentences(page["text"]):
            for piece in cut_long_sentence(sentence, max_chars):
                sentences.append(
                    {"text": piece, "page": page["number"], "kanda": page["kanda"]}
                )

    # Step 2: fill a chunk with sentences until it is full, then start the next one.
    # The new chunk begins with the LAST sentence of the old one (overlap),
    # so an idea is not cut in half.
    chunks = []
    current = []
    size = 0
    for sentence in sentences:
        if current and size + len(sentence["text"]) > max_chars:
            chunks.append(_make_chunk(current, len(chunks)))
            current = current[-1:]  # keep 1 sentence as overlap
            size = len(current[0]["text"])
        current.append(sentence)
        size += len(sentence["text"]) + 1
    if current:
        chunks.append(_make_chunk(current, len(chunks)))
    return chunks


def _make_chunk(sentences, number):
    return Chunk(
        id=f"chunk_{number:05d}",
        text=" ".join(s["text"] for s in sentences),
        page=sentences[0]["page"],  # page where this chunk starts
        kanda=sentences[0]["kanda"],
    )
