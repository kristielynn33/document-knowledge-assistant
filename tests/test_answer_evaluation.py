from dataclasses import replace

from evaluate_answers import EXAMPLE_CASES, review_case


def test_supported_answer_passes_review():
    case = EXAMPLE_CASES[0]

    assert review_case(case) == []


def test_unsupported_question_decline_passes_review():
    case = EXAMPLE_CASES[1]

    assert review_case(case) == []


def test_unknown_citation_fails_review():
    case = replace(
        EXAMPLE_CASES[0],
        citation_ids=("invented-passage",),
    )

    issues = review_case(case)

    assert any("not supplied" in issue for issue in issues)


def test_missing_citation_fails_review():
    case = replace(
        EXAMPLE_CASES[0],
        citation_ids=(),
    )

    issues = review_case(case)

    assert any("requires a citation" in issue for issue in issues)


def test_wrong_status_fails_review():
    case = replace(
        EXAMPLE_CASES[1],
        status="answered",
        citation_ids=("leave-policy-p3",),
    )

    issues = review_case(case)

    assert any("expected status" in issue for issue in issues)


def test_reviewer_can_reject_structurally_valid_answer():
    case = replace(
        EXAMPLE_CASES[0],
        reviewer_supported=False,
    )

    issues = review_case(case)

    assert any("reviewer did not approve" in issue for issue in issues)