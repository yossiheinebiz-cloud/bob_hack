# -*- coding: utf-8 -*-
"""engine/rules/license_unused.py — רישיונות שלא בשימוש"""
import pandas as pd
from engine.models import Finding

RULE_ID  = "LICENSE_UNUSED"
CATEGORY = "licenses"
UNUSED_DAYS    = 30     # כמה ימים ללא שימוש = לא בשימוש
MIN_ANNUAL_ILS = 3000   # חיסכון מינימלי שנתי להציג — מסנן רעש
MIN_UNUSED_PCT = 0.10   # לפחות 10% מהרישיונות לא בשימוש


def check(df: pd.DataFrame) -> list[Finding]:
    """
    מוצא: כלים שמספר הרישיונות בשימוש קטן מהרישיונות ששולמו.
    דורש: seats_paid, seats_used_30d, price_per_seat_ils, tool
    מסנן: חיסכון < MIN_ANNUAL_ILS או אחוז לא-בשימוש < MIN_UNUSED_PCT
    """
    required = {"tool", "seats_paid", "seats_used_30d", "price_per_seat_ils"}
    if not required.issubset(df.columns):
        return []

    findings = []
    for _, row in df.iterrows():
        unused = row["seats_paid"] - row["seats_used_30d"]
        if unused <= 0:
            continue
        pct_unused = unused / row["seats_paid"]
        if pct_unused < MIN_UNUSED_PCT:
            continue
        # חיסכון שנתי: רישיונות מיותרים × מחיר × 12
        annual_saving = unused * row["price_per_seat_ils"] * 12
        if annual_saving < MIN_ANNUAL_ILS:
            continue

        pct_unused = round(unused / row["seats_paid"] * 100)
        findings.append(Finding(
            rule_id       = RULE_ID,
            title         = f"רישיונות {row['tool']} — {unused} מתוך {row['seats_paid']} לא בשימוש ({pct_unused}%)",
            amount_at_risk= annual_saving,
            confidence    = 0.9,
            evidence      = [row.to_dict()],
            action        = f"בטל {unused} רישיונות מיותרים בסבב החידוש הבא. חיסכון: ₪{annual_saving:,.0f}/שנה",
            category      = CATEGORY,
        ))
    return findings
