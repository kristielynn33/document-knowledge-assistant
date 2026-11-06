import json
from collections import Counter
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parent
REVIEWS_FOLDER = PROJECT_FOLDER / "data" / "answer_reviews"


def main() -> int:
    """Display a local summary of manually reviewed responses."""

    review_files = sorted(
        REVIEWS_FOLDER.glob("review_*.json")
    )

    if not review_files:
        print("No saved review files were found.")
        print(f"Folder checked: {REVIEWS_FOLDER}")
        return 1

    records = []

    try:
        for file_path in review_files:
            record = json.loads(
                file_path.read_text(encoding="utf-8")
            )

            if not isinstance(record, dict):
                raise ValueError(
                    f"{file_path.name} does not contain a JSON object."
                )

            required_fields = {
                "question",
                "model_status",
                "reviewer_judgment",
            }

            if not required_fields.issubset(record):
                raise ValueError(
                    f"{file_path.name} is missing required fields."
                )

            if record["model_status"] not in {
                "answered",
                "insufficient_evidence",
            }:
                raise ValueError(
                    f"{file_path.name} has an unexpected model status."
                )

            if record["reviewer_judgment"] not in {
                "APPROVE",
                "REJECT",
            }:
                raise ValueError(
                    f"{file_path.name} has an unexpected review judgment."
                )

            records.append(record)

    except (OSError, ValueError) as error:
        print(f"FAILED: {error}")
        return 1

    judgments = Counter(
        record["reviewer_judgment"]
        for record in records
    )

    statuses = Counter(
        record["model_status"]
        for record in records
    )

    print("LOCAL HUMAN-REVIEW SUMMARY")
    print("No Gemini request was made.\n")

    print(f"Reviewed responses: {len(records)}")
    print(f"Approved by reviewer: {judgments['APPROVE']}")
    print(f"Rejected by reviewer: {judgments['REJECT']}")
    print(f"Model answered: {statuses['answered']}")
    print(
        "Model reported insufficient evidence: "
        f"{statuses['insufficient_evidence']}"
    )

    print("\nREVIEWED QUESTIONS")

    for number, record in enumerate(records, start=1):
        print(f"\n{number}. {record['question']}")
        print(f"   Model status: {record['model_status']}")
        print(
            "   Reviewer judgment: "
            f"{record['reviewer_judgment']}"
        )

    print(
        "\nThese are manually selected, human-reviewed examples. "
        "The counts are not a general accuracy measurement."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())