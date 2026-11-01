# AGENTS.md — איפה הכסף

## מה הפרויקט
מערכת AI שסורקת נתונים כספיים ומוצאת בזבוז, חריגות וחיסכון אפשרי.
בנויה להאקתון IBM Bob 2026 — כל הקוד נכתב בתוך Bob IDE בחשבון ההאקתון.

## מבנה התיקיות

```
bob/
├── AGENTS.md                  ← אתה כאן
├── 00-brief.md                ← רעיון + החלטות
├── 01-spec.md                 ← אפיון מוצר מלא
├── 02-domains.md              ← עולמות תוכן: ארגון, הייטק, בית
├── 03-product-design.md       ← מסכים, עיצוב, מבנה נתונים
├── 04-future-features.md      ← מפת דרכים + חסמי כניסה
├── plans/                     ← תכנוני בנייה לפי שיחה
├── scripts/                   ← run_engine.py, export_findings.py, generate_data.py
├── data/                      ← synthetic/, startup/
├── design/                    ← v2/
└── bob_sessions/              ← צילומי מסך לשיפוט (לא בגיט)
```

## טכנולוגיה

| שכבה | בחירה |
|---|---|
| שפה | Python 3.11+ |
| נתונים | DuckDB על קבצי CSV/JSON |
| API | FastAPI |
| לוח בקרה | HTML + vanilla JS, RTL עברית |
| סוכן | watsonx Orchestrate + MCP tools |
| דוח | HTML → PDF |
| ענן (עתידי) | Google BigQuery, Cloudant |

## כללי כתיבת קוד

- כל כלל במנוע — פונקציה נפרדת בקובץ נפרד תחת `engine/rules/`
- כל פונקציית כלל מחזירה `list[Finding]` — מבנה אחיד
- בדיקת יחידה לכל כלל — חובה לפני merge
- שמות קבצים באנגלית, תוכן ממשק משתמש בעברית
- אין מפתחות API בקוד — רק מ-env vars

## מבנה Finding (ממצא)

```python
Finding(
    rule_id: str,        # "DUP_INVOICE_EXACT"
    title: str,          # "חשבונית כפולה"
    amount_at_risk: float,
    confidence: float,   # 0.0–1.0
    evidence: list[dict],# השורות המקוריות
    action: str,         # "לבדוק עם הספק"
    status: str          # "open" | "reviewed_ok" | "fixed"
)
```

## סדר בנייה (ראה plans/)

1. `plans/01-synthetic-data.md` — מחולל נתונים סינתטיים
2. `plans/02-rules-engine.md` — מנוע כללים: כפילויות + שכר + עלויות
3. `plans/03-dashboard.md` — לוח בקרה + API
4. `plans/05-agent.md` — סוכן watsonx Orchestrate
5. `plans/06-report.md` — דוח PDF

## מה לא לעשות

- לא לשמור נתוני עובדים אמיתיים בגיט
- לא לכתוב API keys בקוד
- לא לשפוט עובד — רק לזהות חריגות בתהליך
- לא לייצר ממצא בלי ראיה (שורה מקורית)
