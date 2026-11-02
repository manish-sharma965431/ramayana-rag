"""CONTROLLER: tools to CHECK that search works (no LLM used here)."""

import config
from models import embedder, vector_store
from views import terminal_view as view
import llm

# Add your own questions to both lists. More questions = a better threshold.
IN_TOPIC = [
    "Who was Rama's father?",
    "Why was Rama sent to the forest?",
    "Who kidnapped Sita?",
    "What did Hanuman do in Lanka?",
    "Who is Jatayu?",
    "How did Ravana die?",
    "Who were the brothers of Rama?",
    "What boon did Kaikeyi ask from Dasharatha?",
    "Who built the bridge to Lanka?",
    "Who is Vibhishana?",
    "Who is Sugriva?",
    "Tell me about Bharata.",
    "Who was Shabari?",
    "What did Sita do in the Ashoka garden?",
]
OFF_TOPIC = [
    "Who won the last cricket world cup?",
    "How do I make pasta?",
    "What is the capital of France?",
    "Write a Python function to sort a list.",
    "Explain quantum computing.",
    "Who is the president of the USA?",
    "What is the weather today?",
    "Tell me a joke.",
    "Who was Zeus in Greek mythology?",
    "Who fought in the Kurukshetra war?",  # hard: Mahabharata
    "Who is Arjuna?",  # hard: Mahabharata
    "How do I invest in the stock market?",
]

# def search_loop():
#     """Type a question, see the best chunks and their scores."""
#     while True:
#         question = view.ask("\nQuestion (press Enter to quit): ")
#         if not question:
#             break
#         hits = vector_store.search(embedder.embed_query(question), config.TOP_K)
#         view.show_hits(hits)


def search_loop():
    """Type a question, get an LLM answer grounded in the best chunks."""
    while True:
        question = view.ask("\nQuestion (press Enter to quit): ")
        if not question:
            break

        hits = vector_store.search(embedder.embed_query(question), config.TOP_K)

        # 1) LLM answer, streamed token by token
        print("\nAnswer: ", end="", flush=True)
        for token in llm.answer_stream(question, hits):
            print(token, end="", flush=True)
        print("\n")

        # 2) Keep your original output as "sources"
        if config.SHOW_SOURCES:
            view.show_hits(hits[:3])


def top_score(question):
    hits = vector_store.search(embedder.embed_query(question), 1)
    return hits[0].score if hits else 0.0


def calibrate():
    """Find the best MIN_SCORE: high enough to block off-topic, low enough to allow real questions."""
    in_scores = [(q, top_score(q)) for q in IN_TOPIC]
    off_scores = [(q, top_score(q)) for q in OFF_TOPIC]

    view.show("\nRamayana questions (should PASS):")
    for question, score in sorted(in_scores, key=lambda x: x[1]):
        view.show(f"  {score:.3f}  {question}")
    view.show("\nOff-topic questions (should be BLOCKED):")
    for question, score in sorted(off_scores, key=lambda x: -x[1]):
        view.show(f"  {score:.3f}  {question}")

    # Try every score as a cut-off and count the mistakes
    best = None
    for cutoff in sorted({s for _, s in in_scores + off_scores}):
        wrongly_blocked = sum(1 for _, s in in_scores if s < cutoff)
        leaked = sum(1 for _, s in off_scores if s >= cutoff)
        mistakes = wrongly_blocked + leaked
        if best is None or mistakes < best[0]:
            best = (mistakes, cutoff, wrongly_blocked, leaked)

    mistakes, cutoff, wrongly_blocked, leaked = best
    total = len(in_scores) + len(off_scores)
    view.show(f"\nBest cut-off: {cutoff:.3f}  ({total - mistakes}/{total} correct)")
    view.show(f"  Real questions wrongly blocked: {wrongly_blocked}")
    view.show(f"  Off-topic questions that got through: {leaked}")
    view.show(f"\nPut this in config.py:   MIN_SCORE = {cutoff:.2f}")
