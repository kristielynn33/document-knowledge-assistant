\# Document Knowledge Assistant



A portfolio prototype that retrieves passages from invented company-policy

documents and proposes answers with citations using Gemini.



The assistant asks for permission before sending a question and retrieved

passages to an external API. Its responses require human review: a valid

citation identifier does not prove that a cited passage supports an answer.



\## How it works



```text

Question

&#x20;  |

&#x20;  v

Local TF-IDF retrieval

&#x20;  |

&#x20;  v

Display candidate passages

&#x20;  |

&#x20;  v

User approves sending them

&#x20;  |

&#x20;  v

Gemini proposes an answer or reports insufficient evidence

&#x20;  |

&#x20;  v

Python validates response structure and citation identifiers

&#x20;  |

&#x20;  v

Display answer and cited source text for review

```



The included policy documents are invented examples, not real company policies.



\## Features



\- Local word-based passage retrieval using TF-IDF.

\- Passage identifiers and source filenames.

\- A browser interface built with Streamlit.

\- Explicit permission before an AI request.

\- Structured response and citation-ID validation.

\- Insufficient-evidence responses.

\- Offline retrieval checks and manual answer reviews.

\- Automated tests using simulated model responses.



\## Requirements



\- Python 3.12.

\- Packages listed in `requirements.txt`.

\- A Gemini API key and an available model for live answers.

\- Internet access for package installation and live API requests.



Local retrieval and automated tests do not require a live Gemini request.



\## Setup on Windows



From this project folder in PowerShell:



```powershell

py -3.12 -m venv .venv

.\\.venv\\Scripts\\python.exe -m pip install -r .\\requirements.txt

```



Create a local `.env` file using `.env.example` as a template. Add your own

Gemini API key and select a model available to your Google project.



Never commit `.env` or share your API key.



\## Run the browser interface



```powershell

.\\.venv\\Scripts\\python.exe -m streamlit run app.py --server.address 127.0.0.1

```



Open the local URL displayed in PowerShell. Keep PowerShell open while using

the application. Press Ctrl+C in PowerShell to stop it.



1\. Enter a question.

2\. Retrieve passages locally.

3\. Review the displayed question and passages.

4\. Send them to Gemini only if authorized.

5\. Review the proposed answer against its cited source text.



A live request may consume billable API quota.



\## Command-line examples



Retrieve passages without calling Gemini:



```powershell

.\\.venv\\Scripts\\python.exe -m retrieval "How many days of paid annual leave do full-time employees receive?"

```



Request an answer after reviewing the passages:



```powershell

.\\.venv\\Scripts\\python.exe -m answer "How many days of paid annual leave do full-time employees receive?"

```



The answer command asks for permission before making an API request.



\## Run the checks



Run the Python tests:



```powershell

.\\.venv\\Scripts\\python.exe -m pytest .\\tests -q

```



At the documented checkpoint, \*\*28 tests passed\*\*. They include simulated

AI responses; they are not a measurement of live model accuracy.



Run the offline retrieval evaluation:



```powershell

.\\.venv\\Scripts\\python.exe -m evaluate\_retrieval

```



Display the local human-review summary:



```powershell

.\\.venv\\Scripts\\python.exe -m summarize\_reviews

```



See `EVALUATION.md` for the small evaluation sample and its limitations.



\## Privacy and security



\- The browser app runs locally when started with `127.0.0.1`; that alone

&#x20; does not make it a secure multi-user service.

\- When approved, the question and displayed passages are sent to Gemini.

\- Use only documents you are authorized to send.

\- Do not use confidential documents in this prototype.

\- Local review files may contain question and passage text; they are

&#x20; excluded from Git by `.gitignore`.

\- Source passages are treated as untrusted in the prompt, but prompt-

&#x20; injection resistance has not been systematically evaluated.



\## Current limitations



\- TF-IDF measures word overlap, not answer confidence.

\- Relevant passages can be missed, and irrelevant passages can be retrieved.

\- Citation-ID validation does not verify factual support.

\- The evaluation set is small and does not establish general accuracy.

## Audio walkthrough

[narration_document_assistant_brief.wav](https://github.com/user-attachments/files/34491904/narration_document_assistant_brief.wav)

This audio overview uses a Windows synthetic voice. It describes the
working pipeline, validation checks, Tableau reporting, and supervised
question-answering features.

This is narration only, not a screen-recorded demonstration.

