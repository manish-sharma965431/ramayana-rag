"""Turns the raw Ramayana text into small chunks that carry their kanda and sarga."""
import re
from dataclasses import dataclass

# A heading is a SHORT line. Change these patterns if your file looks different.
KANDA_RE = re.compile(
    r"^\s*(?:book\s+[ivx\d]+\b.*"
    r"|.*\b(?:bala|ayodhya|aranya|kishkindha|kishkinda|sundara|yuddha|lanka|uttara)"
    r"\s*(?:kanda|kand|kaanda)\b.*)$",
    re.IGNORECASE,
)
SARGA_RE = re.compile(r"^\s*(?:sarga|canto|chapter)\s+[\w\-\.]+.*$", re.IGNORECASE)
MAX_HEADING_LEN = 80


@dataclass
class Chunk:
    id: str
    text: str
    kanda: str
    sarga: str


def split_sections(text: str) -> list[tuple[str, str, str]]:
    """Walk the file line by line and return (kanda, sarga, body) sections."""
    sections: list[tuple[str, str, str]] = []
    kanda, sarga = "Unknown", "Unknown"
    buffer: list[str] = []

    def flush() -> None:
        body = " ".join(" ".join(buffer).split())   # collapse all whitespace
        if body:
            sections.append((kanda, sarga, body))
        buffer.clear()

    for line in text.splitlines():
        s = line.strip()
        if s and len(s) <= MAX_HEADING_LEN and KANDA_RE.match(s):
            flush()
            kanda, sarga = s, "Unknown"
        elif s and len(s) <= MAX_HEADING_LEN and SARGA_RE.match(s):
            flush()
            sarga = s
        elif s:
            buffer.append(s)
    flush()
    return sections


def split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s]


def _hard_split(piece: str, max_chars: int) -> list[str]:
    """Safety net: cut a very long 'sentence' (for example verse without full stops)."""
    if len(piece) <= max_chars:
        return [piece]
    parts, current = [], ""
    for word in piece.split():
        if len(current) + len(word) + 1 > max_chars and current:
            parts.append(current)
            current = ""
        current = f"{current} {word}".strip()
    if current:
        parts.append(current)
    return parts


def pack(sentences: list[str], max_chars: int, overlap_chars: int) -> list[str]:
    """Group sentences into chunks of up to max_chars. Each new chunk starts with the
    last sentence(s) of the previous one (the overlap), so an idea is not cut in half."""
    chunks: list[str] = []
    current: list[str] = []
    size = 0
    for sentence in sentences:
        for piece in _hard_split(sentence, max_chars):
            if current and size + len(piece) + 1 > max_chars:
                chunks.append(" ".join(current))
                tail, tail_size = [], 0
                for s in reversed(current):
                    if tail_size + len(s) > overlap_chars:
                        break
                    tail.insert(0, s)
                    tail_size += len(s) + 1
                current, size = tail, tail_size
            current.append(piece)
            size += len(piece) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks


def chunk_text(text: str, max_chars: int, overlap_chars: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    for kanda, sarga, body in split_sections(text):
        for piece in pack(split_sentences(body), max_chars, overlap_chars):
            chunks.append(Chunk(id=f"c{len(chunks):05d}", text=piece, kanda=kanda, sarga=sarga))
    return chunks