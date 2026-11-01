# Rules — מהנדס כללים (rules-engineer mode)

## לפני כל כלל — בדוק ב-06-payment-problems.md
1. האם הכלל רשום בקטלוג? מה ה-rule_id שלו?
2. מה מקרה החיובי (מוצא בעיה)?
3. מה מקרה השלילי (לא מסמן נתונים תקינים)?
4. מה ה-False Positive הנפוץ ביותר לכלל הזה?

## Finding — תמיד לייבא מ-engine/models.py
```python
from engine.models import Finding
# לא להגדיר Finding מחדש בשום קובץ אחר
```

## Confidence levels — תקן מחייב
```python
1.0   = התאמה מדויקת (אותו מספר חשבונית, אותו סכום)
0.95  = התאמה גבוהה (fuzzy match >95%)
0.85  = סטטיסטי חזק (חריגה > 3 sigma)
0.75  = סטטיסטי (חריגה > 2 sigma)
0.65  = אינדיקטיבי (pattern חשוד, לא ודאי)
< 0.6 = לא לכלול בממצאים — רעש
```

## תבנית כלל מלאה
```python
# engine/rules/dup_invoice_exact.py
import pandas as pd
from engine.models import Finding

RULE_ID = "DUP_INVOICE_EXACT"
RULE_DESC = "אותו ספק ואותו מספר חשבונית שולמו יותר מפעם אחת"

def check(df: pd.DataFrame) -> list[Finding]:
    """
    מוצא: אותו vendor_id + invoice_number עם count > 1.
    False positive אפשרי: חשבונית מבוטלת ומוחזרת — בדוק status != 'cancelled'.
    """
    required_cols = ["vendor_id", "invoice_number", "amount", "date", "row_id"]
    for col in required_cols:
        if col not in df.columns:
            return []  # חסר עמודה — לא להתרסק

    dupes = (
        df[df.get("status", "paid") != "cancelled"]
        .groupby(["vendor_id", "invoice_number"])
        .filter(lambda g: len(g) > 1)
    )

    findings = []
    for (vendor, inv_num), group in dupes.groupby(["vendor_id", "invoice_number"]):
        amount = group["amount"].iloc[0]
        findings.append(Finding(
            rule_id=RULE_ID,
            title=f"חשבונית כפולה — {vendor}",
            amount_at_risk=float(amount),
            confidence=1.0,
            evidence=group.to_dict("records"),
            action="פנה לספק לקבלת זיכוי על התשלום הכפול",
        ))
    return findings
```

## תבנית בדיקה מלאה
```python
# engine/tests/test_dup_invoice_exact.py
import pandas as pd
import pytest
from engine.rules.dup_invoice_exact import check

def make_invoice(vendor, inv_num, amount, date, status="paid"):
    return {"vendor_id": vendor, "invoice_number": inv_num,
            "amount": amount, "date": date, "status": status, "row_id": 1}

class TestDupInvoiceExact:
    def test_finds_exact_duplicate(self):
        df = pd.DataFrame([
            make_invoice("מילגם", "INV-001", 23400, "2026-03-12"),
            make_invoice("מילגם", "INV-001", 23400, "2026-03-15"),
        ])
        findings = check(df)
        assert len(findings) == 1
        assert findings[0].rule_id == "DUP_INVOICE_EXACT"
        assert findings[0].amount_at_risk == 23400
        assert findings[0].confidence == 1.0
        assert len(findings[0].evidence) == 2

    def test_no_false_positive_on_clean_data(self):
        df = pd.DataFrame([
            make_invoice("מילגם", "INV-001", 23400, "2026-03-12"),
            make_invoice("מילגם", "INV-002", 23400, "2026-03-15"),  # מספר שונה
        ])
        assert check(df) == []

    def test_ignores_cancelled_invoices(self):
        df = pd.DataFrame([
            make_invoice("מילגם", "INV-001", 23400, "2026-03-12"),
            make_invoice("מילגם", "INV-001", 23400, "2026-03-15", status="cancelled"),
        ])
        assert check(df) == []

    def test_returns_empty_on_missing_columns(self):
        df = pd.DataFrame([{"vendor": "מילגם"}])  # עמודות חסרות
        assert check(df) == []
```

## DuckDB — מתי להשתמש
```python
# עדיף DuckDB על groupby מורכב:
import duckdb
result = duckdb.execute("""
    SELECT vendor_id, invoice_number, COUNT(*) as cnt, SUM(amount) as total
    FROM df
    WHERE status != 'cancelled'
    GROUP BY vendor_id, invoice_number
    HAVING COUNT(*) > 1
""").df()
```

## סדר בנייה תמיד
1. כתוב בדיקה (test fails — זה בסדר)
2. כתוב כלל מינימלי שמעביר הבדיקה
3. הוסף edge cases לבדיקה
4. שפר את הכלל עד שכל הבדיקות עוברות
5. הרץ על data/synthetic/ — וודא שמוצא את הבעיה השתולה הרלוונטית
