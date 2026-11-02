"""All talking to Ollama lives here (embeddings now, chat in part 2)."""

from functools import lru_cache
import ollama
from ramayana_rag.config import get_settings

HELP = "Is Ollama running (`ollama serve`) and did you run `ollama pull {model}`?"

@lru_cache
def _client() -> ollama.Client:
    return ollama.Client(host=get_settings().ollama_host)


def _prefixes() -> tuple[str, str]:
    # nomic-embed-text was trained with these prefixes and retrieves better with them.
    if get_settings().embed_model.startswith("nomic"):
        return "search_document: ", "search_query: "
    return "", ""


def _embed(texts: list[str]) -> list[list[float]]:
    model = get_settings().embed_model
    try:
        return _client().embed(model=model, input=texts).embeddings
    except Exception as exc:
        raise RuntimeError(
            f"Embedding failed: {exc}. {HELP.format(model=model)}"
        ) from exc


def embed_documents(texts: list[str]) -> list[list[float]]:
    doc_prefix, _ = _prefixes()
    return _embed([doc_prefix + t for t in texts])


def embed_query(text: str) -> list[float]:
    _, query_prefix = _prefixes()
    return _embed([query_prefix + text])[0]
