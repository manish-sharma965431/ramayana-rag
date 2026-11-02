def show(message=""):
    print(message)


def ask(prompt):
    return input(prompt).strip()


def show_hits(hits):
    if not hits:
        print("Nothing found. Did you run ingest?")
    for rank, hit in enumerate(hits, start=1):
        print(f"\n#{rank}  score={hit.score:.3f}  |  {hit.kanda}  |  page {hit.page}")
        print("    " + hit.text[:300] + "...")