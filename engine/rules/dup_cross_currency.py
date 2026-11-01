# -*- coding: utf-8 -*-
"""engine/rules/dup_cross_currency.py — חשבונית כפולה בשתי מטבעות"""
import pandas as pd
from engine.models import Finding

RULE_ID  = "DUP_CROSS_CURRENCY"
CATEGORY = "duplicates"

# שיעורי המרה קבועים — מספיקים לאיתור, לא לחשבונאות
FX_TO_ILS = {
    "USD": 3.70,
    "EUR": 4.05,
    "GBP": 4.70,
    "ILS": 1.00,
}

TOLERANCE = 0.10  # 10% סטייה מותרת בין שתי הגרסאות


def check(df: pd.DataFrame) -> list[Finding]:
    """
    מוצא: אותו invoice_id מאותו vendor מופיע פעמיים במטבעות שונות,
    כאשר הסכומים שקולים (בתוך סטיית TOLERANCE אחרי המרה ל-ILS).

    דורש: invoice_id, vendor_name, amount, currency
    """
    required = {"invoice_id", "vendor_name", "amount", "currency"}
    if not required.issubset(df.columns):
        return []

    active = df[df.get("status", pd.Series(["paid"] * len(df))) != "cancelled"].copy()

    # רק מקרים שבהם אותו invoice_id מופיע ביותר ממטבע אחד
    multi = (active
             .groupby(["vendor_name", "invoice_id"])
             .filter(lambda g: g["currency"].nunique() > 1))

    findings = []
    for (vendor, inv_id), grp in multi.groupby(["vendor_name", "invoice_id"]):
        grp = grp.copy()
        grp["amount_ils"] = grp.apply(
            lambda r: r["amount"] * FX_TO_ILS.get(r["currency"], 1.0), axis=1
        )
        min_ils = grp["amount_ils"].min()
        max_ils = grp["amount_ils"].max()
        if min_ils == 0:
            continue
        if (max_ils - min_ils) / min_ils > TOLERANCE:
            continue  # סכומים שונים מדי — כנראה לא כפול

        amount_at_risk = float(grp["amount_ils"].max())
        currencies = "/".join(sorted(grp["currency"].unique()))
        findings.append(Finding(
            rule_id        = RULE_ID,
            title          = f"חשבונית כפולה בין-מטבעית — {vendor} ({currencies})",
            amount_at_risk = amount_at_risk,
            confidence     = 0.85,
            evidence       = grp.to_dict("records"),
            action         = (
                f"חשבונית {inv_id} שולמה פעמיים: {currencies}. "
                f"פנה ל-{vendor} לקבלת זיכוי על התשלום הכפול."
            ),
            category       = CATEGORY,
        ))
    return findings
