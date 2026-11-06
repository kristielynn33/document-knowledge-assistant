from dataclasses import dataclass
from typing import Literal


Status = Literal["answered", "insufficient_evidence"]


@dataclass(frozen=True)
class ReviewCase:
    """One simulated answer and a human review of that answer."""

    question: str
    supplied_ids: tuple[str, ...]
    status: Status
    answer: str
    citation_ids: tuple[str, ...]
    expected_status: Status

    # A human reviewer records this judgment.
    # It is not calculated by the program.
    reviewer_supported: bool


def review_case(case: ReviewCase) -> list[str]:
    """Check structure and apply the recorded reviewer judgment."""

    issues = []

    if case.status != case.expected_status:
        issues.append("Response status differs from the expected status.")

    supplied = set(case.supplied_ids)
    cited = set(case.citation_ids)

    if len(cited) != len(case.citation_ids):
        issues.append("Duplicate citation IDs.")

    if cited - supplied:
        issues.append("A citation ID was not supplied to the model.")

    if case.status == "answered" and not case.citation_ids:
        issues.append("An answer requires a citation.")

    if (
        case.status == "insufficient_evidence"
        and case.citation_ids
    ):
        issues.append(
            "An insufficient-evidence response should not cite sources."
        )

    if not case.reviewer_supported:
        issues.append("The reviewer did not approve this response.")

    return issues


# These are simulated examples with example human-review labels.
# They do not call Gemini and do not represent a new model run.
EXAMPLE_CASES = [
    ReviewCase(
        question=(
            "How many days of paid annual leave do "
            "full-time employees receive?"
        ),
        supplied_ids=("leave-policy-p2",),
        status="answered",
        answer="Full-time employees receive 15 days per calendar year.",
        citation_ids=("leave-policy-p2",),
        expected_status="answered",
        reviewer_supported=True,
    ),
    ReviewCase(
        question="What is the company policy on parental leave?",
        supplied_ids=("leave-policy-p3", "leave-policy-p4"),
        status="insufficient_evidence",
        answer="The supplied passages do not establish that policy.",
        citation_ids=(),
        expected_status="insufficient_evidence",
        reviewer_supported=True,
    ),
]


def main() -> int:
    print("OFFLINE ANSWER-REVIEW EXAMPLE")
    print("Responses and reviewer judgments are simulated.")
    print("No request will be sent to Gemini.\n")

    passed = 0

    for number, case in enumerate(EXAMPLE_CASES, start=1):
        issues = review_case(case)

        print(f"{number}. {case.question}")
        print(f"   Proposed status: {case.status}")
        print(f"   Proposed answer: {case.answer}")
        print(
            "   Citations: "
            + (", ".join(case.citation_ids) or "none")
        )

        if issues:
            print("   REVIEW FAILED:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            passed += 1
            print("   REVIEW PASSED for this simulated example.")

        print()

    print(f"Simulated cases passing review: {passed}/{len(EXAMPLE_CASES)}")
    print(
        "These results do not measure live model accuracy."
    )

    return 0 if passed == len(EXAMPLE_CASES) else 1


if __name__ == "__main__":
    raise SystemExit(main())