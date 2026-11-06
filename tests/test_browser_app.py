from pathlib import Path
from unittest.mock import MagicMock

import pytest
from streamlit.testing.v1 import AppTest

import answer
from answer import AnswerProposal


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
APP_FILE = PROJECT_FOLDER / "app.py"


@pytest.fixture
def simulated_answer(monkeypatch):
    """Replace the live Gemini request for every test in this file."""

    def make_proposal(question, passages):
        return AnswerProposal(
            status="answered",
            answer="Simulated answer for the browser test.",
            citation_ids=[passages[0].citation_id],
        )

    request = MagicMock(side_effect=make_proposal)

    # app.py imports request_answer from this module.
    monkeypatch.setattr(answer, "request_answer", request)

    return request


def get_button(app, label):
    """Find a button by its visible label."""

    for button in app.button:
        if button.label == label:
            return button

    raise AssertionError(f"Button not found: {label}")


def retrieve_question(app, question):
    """Enter a question and click the local retrieval button."""

    app.text_input[0].set_value(question)

    get_button(
        app,
        "1. Retrieve passages locally",
    ).click().run()

    assert not app.exception


def test_retrieval_does_not_call_gemini(simulated_answer):
    app = AppTest.from_file(str(APP_FILE)).run()

    assert not app.exception

    retrieve_question(
        app,
        "How many days of paid annual leave do "
        "full-time employees receive?",
    )

    passages = app.session_state["reviewed_passages"]

    assert passages
    assert any("15 days" in passage.text for passage in passages)
    assert app.session_state["proposal"] is None
    simulated_answer.assert_not_called()


def test_send_button_requests_one_simulated_answer(simulated_answer):
    app = AppTest.from_file(str(APP_FILE)).run()

    retrieve_question(
        app,
        "How many days of paid annual leave do "
        "full-time employees receive?",
    )

    get_button(
        app,
        "2. SEND these passages to Gemini",
    ).click().run()

    assert not app.exception
    simulated_answer.assert_called_once()

    proposal = app.session_state["proposal"]

    assert proposal is not None
    assert proposal.status == "answered"
    assert proposal.answer == "Simulated answer for the browser test."

    supplied_ids = {
        passage.citation_id
        for passage in app.session_state["reviewed_passages"]
    }

    assert proposal.citation_ids[0] in supplied_ids


def test_new_retrieval_clears_previous_answer(simulated_answer):
    app = AppTest.from_file(str(APP_FILE)).run()

    retrieve_question(
        app,
        "How many days of paid annual leave do "
        "full-time employees receive?",
    )

    get_button(
        app,
        "2. SEND these passages to Gemini",
    ).click().run()

    assert app.session_state["proposal"] is not None
    simulated_answer.assert_called_once()

    retrieve_question(
        app,
        "How many days per week may employees work remotely?",
    )

    assert app.session_state["proposal"] is None
    assert app.session_state["reviewed_question"] == (
        "How many days per week may employees work remotely?"
    )

    # Retrieving the second question must not make another AI request.
    simulated_answer.assert_called_once()