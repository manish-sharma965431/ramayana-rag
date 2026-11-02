"""MODEL: turns text into a list of numbers (a vector) using Ollama.
Texts with similar meaning get similar numbers. That is how search by meaning works."""
import ollama
import config

HELP = "Is Ollama running (ollama serve)? Did you run: ollama pull " + config.EMBED_MODEL


def _prefixes():
    # nomic-embed-text works better when texts start with these labels
    if config.EMBED_MODEL.startswith("nomic"):
        return "search_document: ", "search_query: "
    return "", ""


def _embed(texts):
    try:
        return ollama.embed(model=config.EMBED_MODEL, input=texts).embeddings
    except Exception as error:
        raise RuntimeError(f"Embedding failed: {error}. {HELP}")


def embed_documents(texts):
    """Used when we store the book."""
    doc_prefix, _ = _prefixes()
    return _embed([doc_prefix + t for t in texts])


def embed_query(question):
    """Used for every question the user types."""
    _, query_prefix = _prefixes()
    return _embed([query_prefix + question])[0]