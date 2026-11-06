import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from answer import request_answer
from retrieval import KnowledgeSearch


PROJECT_FOLDER = Path(__file__).resolve().parent


def review_live_answer(question: str) -> int:
    """Request one answer and record a human review locally."""

    question = question.strip()

    if not question or len(question) > 1000:
        raise ValueError(
            "The question must contain 1 to 1000 characters."
        )

    search = KnowledgeSearch(
        PROJECT_FOLDER / "documents"
    )

    matches = search.search(question)

    if not matches:
        print("No passages were retrieved.")
        print("No request was sent to Gemini.")
        return 1

    passages = [passage for passage, score in matches]

    print("The following question and passages will be sent:")
    print(f"\nQuestion: {question}")

    for passage in passages:
        print(f"\n[{passage.citation_id}] {passage.source}")
        print(passage.text)

    print(
        "\nOnly send documents you are authorized to share "
        "with the external API."
    )

    permission = input(
        "Type SEND to request one answer: "
    ).strip()

    if permission != "SEND":
        print("STOPPED: No request was sent.")
        return 1

    print("\nRequesting an answer...", flush=True)
    proposal = request_answer(question, passages)

    print(f"\nModel status: {proposal.status}")
    print(f"Model answer: {proposal.answer}")
    print(
        "Citation IDs: "
        + (", ".join(proposal.citation_ids) or "none")
    )

    print("\nReview the displayed passages and answer.")
    print(
        "For an answered response: check that cited passages "
        "support every claim."
    )
    print(
        "For insufficient evidence: check that declining "
        "the question is appropriate."
    )

    judgment = input(
        "Type APPROVE, REJECT, or SKIP: "
    ).strip().upper()

    if judgment not in {"APPROVE", "REJECT"}:
        print("STOPPED: No review was saved.")
        return 1

    notes = input(
        "Optional review notes, then press Enter: "
    ).strip()

    record = {
        "record_id": uuid4().hex,
        "reviewed_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "question": question,
        "supplied_passages": [
            {
                "citation_id": passage.citation_id,
                "source": passage.source,
                "text": passage.text,
            }
            for passage in passages
        ],
        "model_status": proposal.status,
        "model_answer": proposal.answer,
        "citation_ids": proposal.citation_ids,
        "reviewer_judgment": judgment,
        "reviewer_notes": notes,
    }

    output_folder = PROJECT_FOLDER / "data" / "answer_reviews"
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = (
        output_folder / f"review_{record['record_id']}.json"
    )

    output_file.write_text(
        json.dumps(record, indent=2),
        encoding="utf-8",
    )

    print(f"\nReview saved locally: {output_file}")
    print(
        "One reviewed answer is not an accuracy measurement."
    )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Request and manually review one document answer."
    )

    parser.add_argument(
        "question",
        help="Question about the invented policy documents.",
    )

    args = parser.parse_args()

    try:
        return review_live_answer(args.question)

    except (EOFError, KeyboardInterrupt):
        print("\nSTOPPED by user.")
        return 1

    except (OSError, ValueError, RuntimeError) as error:
        print(f"FAILED: {error}")
        return 1

    except Exception as error:
        print(f"FAILED: operation raised {type(error).__name__}.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())