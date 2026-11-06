import json
from unittest.mock import MagicMock

import pytest

import review_live_answer
from answer import AnswerProposal


@pytest.fixture
def temporary_project(tmp_path, monkeypatch):
    """Use invented documents and a temporary output folder."""

    documents = tmp_path / "documents"
    documents.mkdir()

    (documents / "leave-policy.md").write_text(
        "# Leave Policy\n\n"
        "Full-time employees receive 15 days of annual leave.\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        review_live_answer,
        "PROJECT_FOLDER",
        tmp_path,
    )

    return tmp_path


def provide_answers(monkeypatch, *answers):
    replies = iter(answers)

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(replies),
    )


def test_cancel_before_request_saves_nothing(
    temporary_project,
    monkeypatch,
):
    request = MagicMock()

    monkeypatch.setattr(
        review_live_answer,
        "request_answer",
        request,
    )

    provide_answers(monkeypatch, "CANCEL")

    result = review_live_answer.review_live_answer(
        "How many days of annual leave?",
    )

    assert result == 1
    request.assert_not_called()
    assert not (temporary_project / "data").exists()


def test_approved_review_is_saved_locally(
    temporary_project,
    monkeypatch,
):
    proposal = AnswerProposal(
        status="answered",
        answer="Employees receive 15 days.",
        citation_ids=["leave-policy-p1"],
    )

    request = MagicMock(return_value=proposal)

    monkeypatch.setattr(
        review_live_answer,
        "request_answer",
        request,
    )

    provide_answers(
        monkeypatch,
        "SEND",
        "APPROVE",
        "The cited policy states 15 days.",
    )

    result = review_live_answer.review_live_answer(
        "How many days of annual leave?",
    )

    assert result == 0
    request.assert_called_once()

    review_files = list(
        (
            temporary_project / "data" / "answer_reviews"
        ).glob("review_*.json")
    )

    assert len(review_files) == 1

    record = json.loads(
        review_files[0].read_text(encoding="utf-8")
    )

    assert record["reviewer_judgment"] == "APPROVE"
    assert record["model_status"] == "answered"
    assert record["citation_ids"] == ["leave-policy-p1"]
    assert "15 days" in record["supplied_passages"][0]["text"]


def test_skipped_review_is_not_saved(
    temporary_project,
    monkeypatch,
):
    proposal = AnswerProposal(
        status="insufficient_evidence",
        answer="The supplied passage does not answer that.",
        citation_ids=[],
    )

    monkeypatch.setattr(
        review_live_answer,
        "request_answer",
        MagicMock(return_value=proposal),
    )

    provide_answers(monkeypatch, "SEND", "SKIP")

    result = review_live_answer.review_live_answer(
        "What is the annual leave policy?",
    )

    assert result == 1
    assert not (temporary_project / "data").exists()