from pathlib import Path

from retrieval import KnowledgeSearch, Passage


def find_passages(
    question: str,
    documents_folder: Path,
) -> list[Passage]:
    """Find up to three candidate passages for a question."""

    question = question.strip()

    if not question or len(question) > 1000:
        raise ValueError(
            "The question must contain 1 to 1000 characters."
        )

    search = KnowledgeSearch(documents_folder)
    matches = search.search(question, top_k=3)

    return [
        passage
        for passage, score in matches
    ]