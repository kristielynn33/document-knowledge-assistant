import json
from unittest.mock import MagicMock

import pytest

import answer
from retrieval import Passage


@pytest.fixture
def passages():
    return [
        Passage(
            citation_id="leave-policy-p2",
            source="leave-policy.md",
            text="Full-time employees receive 15 days of annual leave.",
        )
    ]


def test_valid_citation_is_accepted(passages):
    response = json.dumps(
        {
            "status": "answered",
            "answer": "Full-time employees receive 15 days.",
            "citation_ids": ["leave-policy-p2"],
        }
    )

    proposal = answer.validate_proposal(response, passages)

    assert proposal.status == "answered"
    assert proposal.citation_ids == ["leave-policy-p2"]


def test_unknown_citation_is_rejected(passages):
    response = json.dumps(
        {
            "status": "answered",
            "answer": "The policy says 15 days.",
            "citation_ids": ["invented-source-p99"],
        }
    )

    with pytest.raises(ValueError, match="not supplied"):
        answer.validate_proposal(response, passages)


def test_answer_without_citation_is_rejected(passages):
    response = json.dumps(
        {
            "status": "answered",
            "answer": "The policy says 15 days.",
            "citation_ids": [],
        }
    )

    with pytest.raises(ValueError, match="requires"):
        answer.validate_proposal(response, passages)


def test_insufficient_evidence_is_accepted(passages):
    response = json.dumps(
        {
            "status": "insufficient_evidence",
            "answer": "The passages do not contain that information.",
            "citation_ids": [],
        }
    )

    proposal = answer.validate_proposal(response, passages)

    assert proposal.status == "insufficient_evidence"


def test_cancel_does_not_request_answer(tmp_path, monkeypatch):
    document = tmp_path / "leave-policy.md"
    document.write_text(
        "# Leave Policy\n\n"
        "Full-time employees receive 15 days of paid annual leave.\n",
        encoding="utf-8",
    )

    request = MagicMock()

    monkeypatch.setattr(answer, "request_answer", request)
    monkeypatch.setattr("builtins.input", lambda prompt: "CANCEL")

    result = answer.run_question(
        "How much annual leave do full-time employees receive?",
        tmp_path,
    )

    assert result == 1
    request.assert_not_called()