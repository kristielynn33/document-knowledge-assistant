import json

import summarize_reviews


def write_review(folder, filename, record):
    """Write an invented review in a temporary test folder."""

    folder.mkdir(parents=True, exist_ok=True)

    (folder / filename).write_text(
        json.dumps(record),
        encoding="utf-8",
    )


def test_summary_counts_reviews(tmp_path, monkeypatch, capsys):
    reviews_folder = tmp_path / "answer_reviews"

    write_review(
        reviews_folder,
        "review_1.json",
        {
            "question": "How much annual leave?",
            "model_status": "answered",
            "reviewer_judgment": "APPROVE",
        },
    )

    write_review(
        reviews_folder,
        "review_2.json",
        {
            "question": "What is the parental-leave policy?",
            "model_status": "insufficient_evidence",
            "reviewer_judgment": "APPROVE",
        },
    )

    monkeypatch.setattr(
        summarize_reviews,
        "REVIEWS_FOLDER",
        reviews_folder,
    )

    result = summarize_reviews.main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Reviewed responses: 2" in output
    assert "Approved by reviewer: 2" in output
    assert "Rejected by reviewer: 0" in output
    assert "Model answered: 1" in output
    assert "Model reported insufficient evidence: 1" in output
    assert "not a general accuracy measurement" in output


def test_no_reviews_returns_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        summarize_reviews,
        "REVIEWS_FOLDER",
        tmp_path / "empty",
    )

    result = summarize_reviews.main()
    output = capsys.readouterr().out

    assert result == 1
    assert "No saved review files were found" in output


def test_invalid_json_returns_error(tmp_path, monkeypatch, capsys):
    reviews_folder = tmp_path / "answer_reviews"
    reviews_folder.mkdir()

    (reviews_folder / "review_bad.json").write_text(
        "{not valid JSON",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        summarize_reviews,
        "REVIEWS_FOLDER",
        reviews_folder,
    )

    result = summarize_reviews.main()
    output = capsys.readouterr().out

    assert result == 1
    assert "FAILED:" in output


def test_unexpected_judgment_returns_error(
    tmp_path,
    monkeypatch,
    capsys,
):
    reviews_folder = tmp_path / "answer_reviews"

    write_review(
        reviews_folder,
        "review_bad.json",
        {
            "question": "An example question?",
            "model_status": "answered",
            "reviewer_judgment": "MAYBE",
        },
    )

    monkeypatch.setattr(
        summarize_reviews,
        "REVIEWS_FOLDER",
        reviews_folder,
    )

    result = summarize_reviews.main()
    output = capsys.readouterr().out

    assert result == 1
    assert "unexpected review judgment" in output