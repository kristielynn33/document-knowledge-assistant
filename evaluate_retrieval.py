from pathlib import Path

from retrieval import KnowledgeSearch


PROJECT_FOLDER = Path(__file__).resolve().parent

# These expectations apply only to our invented sample policies.
ANSWERABLE_CASES = [
    {
        "question": (
            "How many days of paid annual leave do "
            "full-time employees receive?"
        ),
        "source": "leave-policy.md",
        "expected_text": "15 days",
    },
    {
        "question": (
            "How many unused annual leave days "
            "can employees carry over?"
        ),
        "source": "leave-policy.md",
        "expected_text": "5 unused annual leave days",
    },
    {
        "question": (
            "How many days per week may eligible "
            "employees work remotely?"
        ),
        "source": "remote-work-policy.md",
        "expected_text": "2 days per week",
    },
    {
        "question": (
            "What must remote employees use to "
            "access internal systems?"
        ),
        "source": "remote-work-policy.md",
        "expected_text": "company VPN",
    },
]

UNSUPPORTED_QUESTION = (
    "What is the company policy on parental leave?"
)


def main() -> int:
    """Evaluate whether expected passages appear in the top three."""

    try:
        search = KnowledgeSearch(
            PROJECT_FOLDER / "documents"
        )

        found_count = 0

        print("OFFLINE RETRIEVAL EVALUATION")
        print("No AI requests will be made.\n")

        for number, case in enumerate(
            ANSWERABLE_CASES,
            start=1,
        ):
            matches = search.search(
                case["question"],
                top_k=3,
            )

            expected_found = any(
                passage.source == case["source"]
                and case["expected_text"].lower()
                in passage.text.lower()
                for passage, score in matches
            )

            if expected_found:
                found_count += 1
                status = "FOUND"
            else:
                status = "NOT FOUND"

            print(f"{number}. {case['question']}")
            print(f"   Expected passage in top three: {status}")

            if matches:
                print(
                    f"   First result: "
                    f"[{matches[0][0].citation_id}]"
                )
            else:
                print("   First result: none")

        print(
            f"\nExpected passages found: "
            f"{found_count}/{len(ANSWERABLE_CASES)}"
        )

        print("\nUNSUPPORTED QUESTION — MANUAL REVIEW")
        print(UNSUPPORTED_QUESTION)

        matches = search.search(
            UNSUPPORTED_QUESTION,
            top_k=3,
        )

        if not matches:
            print("No passages were retrieved.")
        else:
            print(
                "Retrieved passages are shown below. "
                "A word match does not mean they answer the question."
            )

            for passage, score in matches:
                print(f"\n[{passage.citation_id}] {passage.source}")
                print(passage.text)

        print(
            "\nThis check measures retrieval for these sample cases. "
            "It does not evaluate generated answers or prove grounding."
        )

        # Make missed expected passages visible as a non-zero result.
        return 0 if found_count == len(ANSWERABLE_CASES) else 1

    except (OSError, ValueError) as error:
        print(f"FAILED: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())