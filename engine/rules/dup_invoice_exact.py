# -*- coding: utf-8 -*-
"""engine/rules/dup_invoice_exact.py — כפילות חשבונית מדויקת"""
import pandas as pd
from engine.models import Finding

RULE_ID   = "DUP_INVOICE_EXACT"
CATEGORY  = "duplicates"


def check(df: pd.DataFrame) -> list[Finding]:
    """
    מוצא: אותו vendor_id + invoice_id עם יותר מרשומה אחת בסטטוס paid.
    False positive: חשבונית מבוטלת ומוחזרת — מסוננת ע"י status != cancelled.
    """
    required = {"invoice_id", "vendor_name", "amount", "invoice_date"}
    if not required.issubset(df.columns):
        return []

    active = df[df.get("status", pd.Series(["paid"] * len(df))) != "cancelled"].copy()
    dupes  = (active
              .groupby(["vendor_name", "invoice_id"])
              .filter(lambda g: len(g) > 1))

    findings = []
    for (vendor, inv_id), grp in dupes.groupby(["vendor_name", "invoice_id"]):
        amount = float(grp["amount"].iloc[0])
        findings.append(Finding(
            rule_id       = RULE_ID,
            title         = f"חשבונית כפולה — {vendor}",
            amount_at_risk= amount,
            confidence    = 1.0,
            evidence      = grp.to_dict("records"),
            action        = "פנה לספק לקבלת זיכוי על התשלום הכפול",
            category      = CATEGORY,
        ))
    return findings
