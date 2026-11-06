from pathlib import Path

import streamlit as st

from answer import request_answer
from browser_helpers import find_passages


PROJECT_FOLDER = Path(__file__).resolve().parent
DOCUMENTS_FOLDER = PROJECT_FOLDER / "documents"


st.set_page_config(
    page_title="Document Knowledge Assistant",
    page_icon="📚",
    layout="centered",
)

st.title("📚 Document Knowledge Assistant")

st.caption(
    "A portfolio prototype using invented company-policy documents."
)

st.info(
    "First retrieve passages locally. You can review them before "
    "choosing whether to send the question and passages to Gemini."
)

# Keep the current question and passages available between button clicks.
if "reviewed_question" not in st.session_state:
    st.session_state.reviewed_question = None

if "reviewed_passages" not in st.session_state:
    st.session_state.reviewed_passages = []

if "proposal" not in st.session_state:
    st.session_state.proposal = None


with st.form("question_form"):
    question = st.text_input(
        "Ask a question about the sample policies",
        placeholder=(
            "Example: How many days of annual leave "
            "do full-time employees receive?"
        ),
        max_chars=1000,
    )

    retrieve_clicked = st.form_submit_button(
        "1. Retrieve passages locally"
    )


if retrieve_clicked:
    # Clear earlier results whenever a new retrieval is requested.
    st.session_state.reviewed_question = None
    st.session_state.reviewed_passages = []
    st.session_state.proposal = None

    try:
        passages = find_passages(
            question,
            DOCUMENTS_FOLDER,
        )

    except (OSError, ValueError) as error:
        st.error(f"Retrieval failed: {error}")

    else:
        if not passages:
            st.warning(
                "No matching passages were found. "
                "No request was sent to Gemini."
            )
        else:
            st.session_state.reviewed_question = question.strip()
            st.session_state.reviewed_passages = passages


current_question = st.session_state.reviewed_question
current_passages = st.session_state.reviewed_passages


if current_passages:
    st.subheader("Passages selected for this question")

    st.write("**Question:**", current_question)

    for passage in current_passages:
        st.markdown(
            f"**[{passage.citation_id}] {passage.source}**"
        )
        st.write(passage.text)

    st.warning(
        "If you continue, Gemini will receive the displayed question "
        "and passage text. Use only documents you are authorized to "
        "send. The request may use billable API quota."
    )

    if st.button(
        "2. SEND these passages to Gemini",
        type="primary",
    ):
        # Remove the previous answer before making a new request.
        st.session_state.proposal = None

        try:
            with st.spinner("Requesting a proposed answer..."):
                proposal = request_answer(
                    current_question,
                    current_passages,
                )

        except Exception as error:
            # Avoid displaying keys or the full request in the browser.
            st.error(
                "The answer request failed: "
                f"{type(error).__name__}. "
                "No answer is displayed."
            )

        else:
            st.session_state.proposal = proposal


proposal = st.session_state.proposal

if proposal is not None:
    if proposal.status == "insufficient_evidence":
        st.subheader("Insufficient evidence")
        st.write(proposal.answer)

    else:
        st.subheader("Proposed answer")
        st.write(proposal.answer)

        passages_by_id = {
            passage.citation_id: passage
            for passage in current_passages
        }

        st.subheader("Cited sources")

        for citation_id in proposal.citation_ids:
            passage = passages_by_id[citation_id]

            st.markdown(
                f"**[{citation_id}] {passage.source}**"
            )
            st.write(passage.text)

        st.warning(
            "Review the cited text. A valid citation ID does not "
            "guarantee that the passage supports the answer."
        )


st.divider()
st.caption(
    "Retrieval scores are not confidence percentages. "
    "This prototype is not intended for confidential documents "
    "or production decisions."
)