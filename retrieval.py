import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_FOLDER = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Passage:
    """A source passage with an identifier for later citations."""

    citation_id: str
    source: str
    text: str


def load_passages(documents_folder: Path) -> list[Passage]:
    """Load paragraphs while excluding normal and escaped headings."""

    passages = []

    for document_path in sorted(documents_folder.glob("*.md")):
        content = document_path.read_text(
            encoding="utf-8-sig"
        ).strip()

        cleaned_lines = []

        for line in content.splitlines():
            # Recognize both:
            # ## Annual leave allowance
            # \## Annual leave allowance
            heading_candidate = line.strip().lstrip("\\")

            if re.match(
                r"^#{1,6}(?:\s|$)",
                heading_candidate,
            ):
                # Preserve a paragraph boundary where a heading stood.
                cleaned_lines.append("")
            else:
                cleaned_lines.append(line)

        cleaned_content = "\n".join(cleaned_lines)
        blocks = re.split(r"\n\s*\n", cleaned_content)

        passage_number = 0

        for block in blocks:
            text = " ".join(block.split())

            if not text:
                continue

            passage_number += 1

            passages.append(
                Passage(
                    citation_id=(
                        f"{document_path.stem}-p{passage_number}"
                    ),
                    source=document_path.name,
                    text=text,
                )
            )

    if not passages:
        raise ValueError(
            "No policy passages found. Add Markdown documents "
            "to the documents folder."
        )

    return passages


class KnowledgeSearch:
    """Retrieve candidate passages using a local TF-IDF index."""

    def __init__(self, documents_folder: Path):
        self.passages = load_passages(documents_folder)

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
        )

        self.document_matrix = self.vectorizer.fit_transform(
            [passage.text for passage in self.passages]
        )

    def search(
        self,
        question: str,
        *,
        top_k: int = 3,
    ) -> list[tuple[Passage, float]]:
        """Return up to top_k passages with positive similarity."""

        question = question.strip()

        if not question:
            raise ValueError("The question must not be empty.")

        if not 1 <= top_k <= 5:
            raise ValueError("top_k must be between 1 and 5.")

        question_vector = self.vectorizer.transform([question])

        scores = cosine_similarity(
            question_vector,
            self.document_matrix,
        ).ravel()

        ranked_indices = sorted(
            range(len(self.passages)),
            key=lambda index: (
                -float(scores[index]),
                self.passages[index].citation_id,
            ),
        )

        matches = [
            (
                self.passages[index],
                float(scores[index]),
            )
            for index in ranked_indices
            if scores[index] > 0
        ]

        return matches[:top_k]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search the local policy documents."
    )

    parser.add_argument(
        "question",
        help="The question used to retrieve source passages.",
    )

    args = parser.parse_args()

    try:
        search = KnowledgeSearch(
            PROJECT_FOLDER / "documents"
        )

        matches = search.search(args.question)

    except (OSError, ValueError) as error:
        print(f"FAILED: {error}")
        return 1

    if not matches:
        print("No matching passages found.")
        print("No answer was generated.")
        return 0

    print("Retrieved source passages:")
    print(
        "These are document excerpts, "
        "not an AI-generated answer.\n"
    )

    for passage, score in matches:
        print(f"[{passage.citation_id}]")
        print(f"Source: {passage.source}")
        print(passage.text)
        print(f"Retrieval score: {score:.3f}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())