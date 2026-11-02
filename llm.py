import ollama
import config

LLM_MODEL = getattr(config, "LLM_MODEL", "llama3.2:3b")
MIN_SCORE = getattr(config, "MIN_SCORE", 0.60)
MAX_CONTEXT_CHARS = getattr(config, "MAX_CONTEXT_CHARS", 6000)

SYSTEM_PROMPT = (
    "You are an expert on the Ramayana. Answer the question using ONLY the "
    "context given. If the context does not contain the answer, reply exactly: "
    "'I could not find this in the provided text.' "
    "Keep the answer short and direct (1-3 sentences). "
    "Mention page numbers like (page 123) for the facts you use."
)


def build_context(hits):
    parts, total = [], 0
    for h in hits:
        if h.score < config.MIN_SCORE:
            continue
        chunk = f"[page {h.page}] {h.text.strip()}"
        if total + len(chunk) > config.MAX_CONTEXT_CHARS:
            break
        parts.append(chunk)
        total += len(chunk)
    return "\n\n".join(parts)


def answer_stream(question, hits):
    context = build_context(hits)
    if not context:
        yield "I could not find this in the provided text."
        return

    stream = ollama.chat(
        model=config.LLM_MODEL,
        stream=True,
        options={"temperature": 0.1, "num_ctx": 4096, "num_predict": 200},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:",
            },
        ],
    )
    for part in stream:
        yield part["message"]["content"]
