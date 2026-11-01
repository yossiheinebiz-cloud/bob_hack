# bob_sessions — IBM Bob Hackathon 2026 Submission

## Project: איפה הכסף (Where Is the Money)

All code in this project was written inside **IBM Bob IDE** using the Agent mode.

---

## Session Log

| # | Date | Description | Output |
|---|------|-------------|--------|
| 1 | 01/11/2026 | Project brief, spec, domain design | `00-brief.md`, `01-spec.md`, `02-domains.md` |
| 2 | 01/11/2026 | Product design, screens, rules catalog | `03-product-design.md` through `06-payment-problems.md` |
| 3 | 01/11/2026 | Privacy compliance doc (Amendment 13) | `07-privacy-compliance.md` |
| 4 | 01/11/2026 | Bob configuration: modes, rules, MCP | `.bob/` directory — 4 custom modes, 7 MCP connectors |
| 5 | 01/11/2026 | Engine: models, rules registry, 4 rules | `engine/models.py`, `engine/rules/` |
| 6 | 01/11/2026 | Synthetic data generator (10 planted issues) | `scripts/generate_data.py`, `data/synthetic/*.csv` |
| 7 | 01/11/2026 | Run engine — 5 findings, ₪205K | `scripts/run_engine.py`, `scripts/export_findings.py` |
| 8 | 01/11/2026 | Dashboard v1 (RTL, dark, findings table) | `dashboard/index.html` |
| 9 | 01/11/2026 | Pitch deck v1 → v2 (redesigned) | `pitch/deck.html` |
| 10 | 01/11/2026 | 6 new rules: DUP_CROSS_CURRENCY, INVOICE_SPLITTING, PAYROLL_DUPLICATE_BANK, LICENSE_DEPARTED, LICENSE_DUPLICATE_FUNC, AUTO_RENEWAL_JUMP | `engine/rules/*.py` |
| 11 | 01/11/2026 | Dashboard v2 — War Room layout, live side panel | `dashboard/index.html` |
| 12 | 01/11/2026 | FastAPI backend | `api/main.py` |
| 13 | 01/11/2026 | Unit tests — 26 tests, 26 passed | `engine/tests/test_rules.py` |

---

## Engine Results (Latest Run — 01/11/2026 15:02)

```
Rules:      10
Findings:   34
At Risk:    ₪2,580,297
Run time:   1.8s
Data:       91 employees · 488 invoices · 15 tools · 192 cloud rows
```

### Top 6 High-Confidence Findings

| Finding | Category | Confidence | Amount |
|---------|----------|-----------|--------|
| שכר אחרי סיום העסקה — EMP1046 | payroll | 100% | ₪72,000 |
| חשבונית כפולה בין-מטבעית — AWS Israel | duplicates | 85% | ₪44,400 |
| חשבונית כפולה — מילגם בע"מ | duplicates | 100% | ₪23,400 |
| שרת זומבי — ec2-staging | cloud | 95% | ₪51,969 |
| HubSpot CRM +32% בחידוש | licenses | 90% | ₪13,968 |
| Figma 8/14 רישיונות לא בשימוש | licenses | 90% | ₪13,440 |

---

## Test Results

```
26 passed, 0 failed — engine/tests/test_rules.py
Python 3.13.1 · pytest 9.2.0
```

---

## What Was Built with IBM Bob

| Component | File | Status |
|-----------|------|--------|
| Product spec | `01-spec.md` | ✅ |
| 30+ rule catalog | `06-payment-problems.md` | ✅ |
| Privacy compliance | `07-privacy-compliance.md` | ✅ |
| 4 custom Bob modes | `.bob/custom_modes.yaml` | ✅ |
| 7 MCP connectors | `.bob/mcp.json` | ✅ |
| Engine: 10 rules | `engine/rules/*.py` | ✅ |
| Synthetic data | `scripts/generate_data.py` | ✅ |
| FastAPI backend | `api/main.py` | ✅ |
| Unit tests (26) | `engine/tests/test_rules.py` | ✅ |
| Dashboard (War Room) | `dashboard/index.html` | ✅ |
| Investor pitch deck | `pitch/deck.html` | ✅ |

---

*All code written exclusively within IBM Bob IDE · Enterprise Plan*
