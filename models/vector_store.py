"""MODEL: the vector database (ChromaDB). Saves chunks and finds the ones closest in meaning."""
from dataclasses import dataclass
import chromadb
import config


@dataclass
class Hit:
    text: str
    page: int
    kanda: str
    score: float        # 1.0 = same meaning, close to 0 = unrelated


def _client():
    return chromadb.PersistentClient(path=config.CHROMA_FOLDER)      # saved on disk


def _collection():
    return _client().get_or_create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},          # compare by meaning-angle (cosine)
    )


def reset():
    """Delete old data, so running ingest twice never makes duplicates."""
    try:
        _client().delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass            # nothing to delete the first time


def save(chunks, vectors):
    _collection().add(
        ids=[c.id for c in chunks],
        documents=[c.text for c in chunks],
        embeddings=vectors,
        metadatas=[{"page": c.page, "kanda": c.kanda} for c in chunks],
    )


def search(query_vector, how_many):
    collection = _collection()
    total = collection.count()
    if total == 0:
        return []
    result = collection.query(
        query_embeddings=[query_vector],
        n_results=min(how_many, total),
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for text, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        score = round(1 - distance, 4)              # distance small = score high
        hits.append(Hit(text=text, page=meta["page"], kanda=meta["kanda"], score=score))
    return hits         # best match first