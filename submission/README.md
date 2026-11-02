# Where Is the Money (איפה הכסף): hackathon submission

Submission for *From \<bob\> to Business Impact: The AI Coding Challenge* (IBM Bob, Israel, 2026).

Where Is the Money scans a company's financial and usage data and returns findings with an amount at risk, a confidence score, the original rows as evidence, and one recommended action.

## Submission documents

| Document | Contents |
|---|---|
| [form-text.txt](form-text.txt) | Problem and solution statement, technology statement, and links, ready to paste into the form |
| [submission-statements.pdf](submission-statements.pdf) | The same text as a PDF |
| [bob_sessions/](../bob_sessions/) | Bob task session screenshots |

## Try it

| What | Link | Status |
|---|---|---|
| Findings dashboard (Hebrew) | https://eifo-money.fit/dashboard/ | Shows exported engine output |
| Design prototype (Hebrew) | https://eifo-money.fit/design/v2/ | Shows the target product using demo data; not connected to the engine |

## Run the engine

Requires Python 3.11 or later.

```bash
pip install -r requirements.txt
python scripts/run_engine.py
python -m pytest -q engine/tests
```

The engine prints 34 findings from `data/synthetic/`, and all 26 tests should pass.

## What is built and what is planned

| Area | Status |
|---|---|
| Rules engine with 10 rules and 26 unit tests | Working |
| Hebrew findings dashboard | Working and deployed; reads an exported findings file |
| CI checks and Docker deployment | Working |
| Synthetic test dataset with 155,263 rows and 26 planted issues | Ready; the engine does not read it yet |
| FastAPI layer | In progress; not deployed, and the synthetic-data scan endpoint has a known bug |
| Full catalogue of 33 rules | Specified; 10 are built |
| watsonx Orchestrate agent and MCP server | Specified; not built |

All company data in this repository is synthetic. Monetary figures are test results, not results from a real customer.
