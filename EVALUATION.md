
Document Knowledge Assistant: Evaluation

SCOPE

This is an early evaluation of a document assistant using two invented
company-policy documents. The results do not establish general accuracy
or production readiness.

OFFLINE RETRIEVAL

The TF-IDF search retrieves passages based on word similarity. For four
sample questions, the expected passage appeared in the top three:

- Full-time annual leave allowance.
- Annual leave carryover.
- Remote-work allowance.
- Remote access requirements.

Result: 4 of 4 expected passages found in the top three.

An unsupported question about parental leave retrieved passages about
annual leave and remote-work security. These passages did not establish
a parental-leave policy. A word match is not proof that a passage
answers a question.

MANUALLY REVIEWED LIVE RESPONSES

1. Annual-leave question: the model answered 15 days and cited the
   supporting passage. Reviewer judgment: APPROVE.

2. Parental-leave question: the model reported insufficient evidence.
   Reviewer judgment: APPROVE.

The parental-leave judgment was initially marked REJECT by mistake and
then corrected locally after the reviewer confirmed the intended judgment.

These are two selected examples, not a general accuracy measurement.

LOCAL REVIEW RECORDS

The review tool saves the question, supplied passages, model response,
citations, reviewer judgment, and notes under data/answer_reviews/.

These files remain local and are excluded by .gitignore. They can contain
document text, so only authorized data should be used.

The summary tool displays review counts; it does not establish whether
a reviewer made the correct judgment.

AUTOMATED CHECKS

At this checkpoint, 25 Python tests passed. They cover retrieval,
heading handling, citation-ID validation, cancellation, simulated review
behavior, review saving, and review-summary behavior.

These tests do not establish the quality or safety of live Gemini answers.

LIMITATIONS

- A valid citation ID does not prove the cited text supports an answer.
- A TF-IDF score is not a confidence percentage.
- Retrieval can return irrelevant passages.
- Results may vary between requests or model versions.
- Prompt-injection resistance has not been systematically evaluated.
- Two live reviewed responses are insufficient for an accuracy claim.
- Production security, latency, cost, and business impact have not
  been measured.

NEXT EVALUATION WORK

Expand the question set, review answers against their cited text, test
ambiguous and unsupported questions, and evaluate adversarial
instructions using invented documents.