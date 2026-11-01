# -*- coding: utf-8 -*-
"""engine/rules/cloud_zombie.py — שרת ענן ללא תעבורה"""
import pandas as pd
from engine.models import Finding

RULE_ID        = "CLOUD_ZOMBIE"
CATEGORY       = "cloud"
IDLE_MONTHS    = 2      # חודשים רצופים ללא תעבורה
MIN_MONTHLY_ILS= 1000   # עלות מינימום להתראה


def check(df: pd.DataFrame) -> list[Finding]:
    """
    מוצא: שירותי ענן עם עלות > 0 אבל traffic_gb == 0 למשך IDLE_MONTHS חודשים רצופים.
    דורש: service, month, cost_ils, traffic_gb
    """
    required = {"service", "month", "cost_ils", "traffic_gb"}
    if not required.issubset(df.columns):
        return []

    df = df.copy()
    df["month"] = pd.to_datetime(df["month"])
    df = df.sort_values(["service", "month"])

    findings = []
    for service, grp in df.groupby("service"):
        # בדוק N חודשים רצופים ללא תעבורה
        grp = grp.reset_index(drop=True)
        idle_streak = 0
        idle_rows   = []
        for _, row in grp.iterrows():
            if row["traffic_gb"] == 0 and row["cost_ils"] > 0:
                idle_streak += 1
                idle_rows.append(row.to_dict())
            else:
                idle_streak = 0
                idle_rows   = []

        if idle_streak >= IDLE_MONTHS:
            monthly_cost = float(pd.Series([r["cost_ils"] for r in idle_rows]).mean())
            if monthly_cost < MIN_MONTHLY_ILS:
                continue
            annual_waste = monthly_cost * 12
            findings.append(Finding(
                rule_id        = RULE_ID,
                title          = f"שרת זומבי — {service}",
                amount_at_risk = annual_waste,
                confidence     = 0.95,
                evidence       = idle_rows[-IDLE_MONTHS:],
                action         = f"שרת {service} פועל {idle_streak} חודשים ללא תעבורה. עלות חודשית: ₪{monthly_cost:,.0f}. כבה או הקטן.",
                category       = CATEGORY,
            ))
    return findings
