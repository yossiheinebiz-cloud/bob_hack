# -*- coding: utf-8 -*-
"""engine/rules/license_departed.py — רישיונות של עובדים שעזבו"""
import pandas as pd
from engine.models import Finding

RULE_ID  = "LICENSE_DEPARTED"
CATEGORY = "licenses"

# אם אחוז הרישיונות "המשוחררים" קטן מזה — לא מדווחים
MIN_DEPARTED_PCT  = 0.03   # 3% מהרישיונות
MIN_ANNUAL_ILS    = 1_200  # חיסכון שנתי מינימלי להצגה


def check(licenses: pd.DataFrame, employees: pd.DataFrame) -> list[Finding]:
    """
    מוצא: כלים שבהם seats_paid > seats_used_30d, וכאשר מספר העובדים שסיימו
    מסביר את הפער — כלומר יש רישיונות פעילים לעובדים שכבר לא כאן.

    גישה פשוטה: אם seats_paid - seats_used_30d >= מספר עובדים שסיימו לאחרונה,
    כנראה שלא בוטלו הרישיונות שלהם.

    דורש:
      licenses:  tool, seats_paid, seats_used_30d, price_per_seat_ils
      employees: status, end_date
    """
    req_lic = {"tool", "seats_paid", "seats_used_30d", "price_per_seat_ils"}
    req_emp = {"status", "end_date"}
    if not req_lic.issubset(licenses.columns) or not req_emp.issubset(employees.columns):
        return []

    # כמה עובדים סיימו ב-90 יום האחרונים
    departed = employees[
        (employees["status"] == "terminated") &
        employees["end_date"].notna() &
        (employees["end_date"] != "")
    ].copy()

    if departed.empty:
        return []

    departed["end_date_dt"] = pd.to_datetime(departed["end_date"], errors="coerce").dt.date
    import datetime
    cutoff = datetime.date.today() - datetime.timedelta(days=180)
    recent_departed = len(departed[departed["end_date_dt"] >= cutoff])

    if recent_departed == 0:
        return []

    findings = []
    for _, row in licenses.iterrows():
        unused = int(row["seats_paid"]) - int(row["seats_used_30d"])
        if unused <= 0:
            continue
        if unused / row["seats_paid"] < MIN_DEPARTED_PCT:
            continue

        # כמה מהבלתי-מנוצלים עשויים להיות של עובדים שעזבו
        suspected = min(unused, recent_departed)
        if suspected == 0:
            continue

        annual_saving = suspected * row["price_per_seat_ils"] * 12
        if annual_saving < MIN_ANNUAL_ILS:
            continue

        findings.append(Finding(
            rule_id        = RULE_ID,
            title          = f"רישיונות {row['tool']} — {suspected} עשויים שייכים לעובדים שעזבו",
            amount_at_risk = float(annual_saving),
            confidence     = 0.80,
            evidence       = [row.to_dict()],
            action         = (
                f"בדוק עם IT/HR אם רישיונות {row['tool']} בוטלו לאחר עזיבת "
                f"{recent_departed} עובדים ב-6 החודשים האחרונים. "
                f"חיסכון פוטנציאלי: ₪{annual_saving:,.0f}/שנה."
            ),
            category       = CATEGORY,
        ))
    return findings
