# -*- coding: utf-8 -*-
"""engine/rules/auto_renewal_jump.py — קפיצת מחיר בחידוש אוטומטי"""
import pandas as pd
from engine.models import Finding

RULE_ID          = "AUTO_RENEWAL_JUMP"
CATEGORY         = "licenses"

MIN_JUMP_PCT     = 0.15   # קפיצה של לפחות 15% בין שנה לשנה
MIN_ANNUAL_ILS   = 5_000  # גודל מינימלי לממצא


def check(df: pd.DataFrame) -> list[Finding]:
    """
    מוצא: כלים שבהם price_change_pct > MIN_JUMP_PCT בחידוש האחרון.
    עלות השוק הוגן (prev_year_price × seats_paid) מול עלות הנוכחית.

    דורש: tool, price_per_seat_ils, prev_year_price, seats_paid, renewal_date
    """
    required = {"tool", "price_per_seat_ils", "prev_year_price", "seats_paid"}
    if not required.issubset(df.columns):
        return []

    findings = []
    for _, row in df.iterrows():
        curr_price = float(row["price_per_seat_ils"])
        prev_price = float(row["prev_year_price"])

        if prev_price <= 0:
            continue

        jump_pct = (curr_price - prev_price) / prev_price
        if jump_pct < MIN_JUMP_PCT:
            continue

        seats = int(row["seats_paid"])
        annual_excess = (curr_price - prev_price) * seats * 12
        if annual_excess < MIN_ANNUAL_ILS:
            continue

        renewal_str = str(row.get("renewal_date", ""))
        renewal_note = f" (חידוש: {renewal_str})" if renewal_str else ""

        findings.append(Finding(
            rule_id        = RULE_ID,
            title          = f"קפיצת מחיר בחידוש — {row['tool']} (+{round(jump_pct*100)}%)",
            amount_at_risk = float(annual_excess),
            confidence     = 0.90,
            evidence       = [row.to_dict()],
            action         = (
                f"{row['tool']} עלה ב-{round(jump_pct*100)}% בחידוש האחרון "
                f"(₪{prev_price:.0f} → ₪{curr_price:.0f}/רישיון){renewal_note}. "
                f"בקש הצעת מחיר מתחרה לפני הזדמנות הוידוא הבאה. "
                f"עלות עודפת: ₪{annual_excess:,.0f}/שנה."
            ),
            category       = CATEGORY,
        ))
    return findings
