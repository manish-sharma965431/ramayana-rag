"""All settings in one place. Change a value here, nothing else needs to change."""

PDF_FILE = "data/ramayana.pdf"  # your Ramayana PDF
CHROMA_FOLDER = "storage/chroma"  # where the vector database is saved
COLLECTION_NAME = "ramayana"

# EMBED_MODEL = "nomic-embed-text"  # turns text into numbers (free, local, via Ollama)
# LLM_MODEL = "llama3.2:3b"  # answers questions (used in Stage 2)

LLM_MODEL = "qwen3.5:9b"
EMBED_MODEL = "qwen3-embedding:0.6b"

CHUNK_SIZE = 900
CHUNK_OVERLAP = 180
TOP_K = 8

MIN_SCORE = 0.60
MAX_CONTEXT_CHARS = 6000
SHOW_SOURCES = True
