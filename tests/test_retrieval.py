import pytest

from retrieval import KnowledgeSearch


@pytest.fixture
def search_index(tmp_path):
    """Create an index from invented temporary documents."""

    leave_document = tmp_path / "leave-policy.md"

    leave_document.write_text(
        "# Leave Policy\n\n"
        "Full-time employees receive 15 days of paid annual "
        "leave per calendar year.\n\n"
        "Employees may carry over up to 5 unused annual "
        "leave days into the next calendar year.\n",
        encoding="utf-8",
    )

    remote_document = tmp_path / "remote-work-policy.md"

    remote_document.write_text(
        "# Remote Work Policy\n\n"
        "Eligible employees may work remotely up to 2 days "
        "per week with manager approval.\n",
        encoding="utf-8",
    )

    return KnowledgeSearch(tmp_path)


def test_annual_leave_question_finds_allowance(search_index):
    matches = search_index.search(
        "How many days of paid annual leave do "
        "full-time employees receive?"
    )

    assert matches

    passage, score = matches[0]

    assert passage.source == "leave-policy.md"
    assert "15 days" in passage.text
    assert passage.citation_id == "leave-policy-p1"
    assert score > 0


def test_remote_work_question_finds_policy(search_index):
    matches = search_index.search(
        "How many days per week may employees work remotely?"
    )

    assert matches

    passage, score = matches[0]

    assert passage.source == "remote-work-policy.md"
    assert "2 days" in passage.text
    assert score > 0


def test_unrelated_words_return_no_passages(search_index):
    matches = search_index.search(
        "volcano eruption"
    )

    assert matches == []


def test_empty_question_is_rejected(search_index):
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        search_index.search("   ")


def test_empty_document_folder_is_rejected(tmp_path):
    with pytest.raises(
        ValueError,
        match="No policy passages",
    ):
        KnowledgeSearch(tmp_path)


@pytest.mark.parametrize(
    "heading_prefix",
    ["#", r"\#"],
    ids=["normal_headings", "escaped_headings"],
)
def test_heading_lines_are_not_indexed(
    tmp_path,
    heading_prefix,
):
    document = tmp_path / "leave-policy.md"

    # Deliberately omit blank lines between headings and text.
    document.write_text(
        f"{heading_prefix} Leave Policy\n"
        f"{heading_prefix}# Annual leave allowance\n"
        "Employees receive 15 days of paid annual leave.\n",
        encoding="utf-8",
    )

    search = KnowledgeSearch(tmp_path)

    # Only the policy text should become a passage.
    assert len(search.passages) == 1

    passage = search.passages[0]

    assert passage.text == (
        "Employees receive 15 days of paid annual leave."
    )
    assert passage.citation_id == "leave-policy-p1"
    assert passage.source == "leave-policy.md"