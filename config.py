"""All settings in one place. Change a value here, nothing else needs to change."""

PDF_FILE = "data/ramayana.pdf"  # your Ramayana PDF
CHROMA_FOLDER = "storage/chroma"  # where the vector database is saved
COLLECTION_NAME = "ramayana"

EMBED_MODEL = "nomic-embed-text"  # turns text into numbers (free, local, via Ollama)
LLM_MODEL = "llama3.2:3b"  # answers questions (used in Stage 2)

CHUNK_SIZE = 600
CHUNK_OVERLAP = 120

MIN_SCORE = 0.60
MAX_CONTEXT_CHARS = 6000
TOP_K = 6
SHOW_SOURCES = True
