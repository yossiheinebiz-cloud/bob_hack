# -*- coding: utf-8 -*-
"""engine/rules/invoice_splitting.py — פיצול חשבוניות מתחת לסף אישור"""
import pandas as pd
from itertools import combinations
from engine.models import Finding

RULE_ID       = "INVOICE_SPLITTING"
CATEGORY      = "duplicates"

THRESHOLD_ILS = 50_000   # סף אישור סמנכ"ל — חשבוניות מעל זה דורשות אישור
MIN_INVOICES  = 3        # מינימום חשבוניות בחלון
WINDOW_DAYS   = 45       # חלון זמן בימים לבדיקה
MIN_TOTAL_ILS = 100_000  # סכום כולל מינימלי להצגת ממצא


def check(df: pd.DataFrame) -> list[Finding]:
    """
    מוצא: ספק שהוציא 3+ חשבוניות בתקופה קצרה שכל אחת מתחת ל-THRESHOLD,
    אבל הסכום הכולל שלהן עובר אותו — סימן לפיצול מכוון.

    דורש: vendor_name, amount, invoice_date
    """
    required = {"vendor_name", "amount", "invoice_date"}
    if not required.issubset(df.columns):
        return []

    active = df[df.get("status", pd.Series(["paid"] * len(df))) != "cancelled"].copy()
    active["invoice_date"] = pd.to_datetime(active["invoice_date"])

    findings = []

    for vendor, grp in active.groupby("vendor_name"):
        # רק חשבוניות מתחת לסף
        below = grp[grp["amount"] < THRESHOLD_ILS].sort_values("invoice_date")
        if len(below) < MIN_INVOICES:
            continue

        # חפש חלון WINDOW_DAYS שבו הסכום הכולל עובר את הסף
        rows = below.reset_index(drop=True)
        found = set()

        for i in range(len(rows)):
            window = rows[
                (rows["invoice_date"] >= rows.loc[i, "invoice_date"]) &
                (rows["invoice_date"] <= rows.loc[i, "invoice_date"] + pd.Timedelta(days=WINDOW_DAYS))
            ]
            if len(window) < MIN_INVOICES:
                continue
            total = float(window["amount"].sum())
            if total < MIN_TOTAL_ILS:
                continue

            key = frozenset(window.index)
            if key in found:
                continue
            found.add(key)

            findings.append(Finding(
                rule_id        = RULE_ID,
                title          = f"פיצול חשבוניות חשוד — {vendor}",
                amount_at_risk = total,
                confidence     = 0.75,
                evidence       = window.to_dict("records"),
                action         = (
                    f"{len(window)} חשבוניות של {vendor} בחלון 45 יום, "
                    f"סה\"כ ₪{total:,.0f} — כל אחת מתחת לסף האישור (₪{THRESHOLD_ILS:,}). "
                    f"בדוק מול הספק אם מדובר בעבודה אחת שפוצלה."
                ),
                category       = CATEGORY,
            ))
            break  # ממצא אחד לכל ספק

    return findings
