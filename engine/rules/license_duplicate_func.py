# -*- coding: utf-8 -*-
"""engine/rules/license_duplicate_func.py — כלים עם פונקציונליות כפולה"""
import pandas as pd
from engine.models import Finding

RULE_ID  = "LICENSE_DUPLICATE_FUNC"
CATEGORY = "licenses"

# קבוצות כלים בעלי פונקציונליות חופפת
# כל קבוצה: (תיאור, [שמות כלים])
OVERLAP_GROUPS = [
    ("ניהול פרויקטים",     ["Jira", "Monday.com", "Asana", "ClickUp", "Linear", "Basecamp"]),
    ("תקשורת פנים-ארגונית",["Slack", "Microsoft Teams", "Google Chat", "Discord"]),
    ("מסמכים ושיתוף",     ["Notion", "Confluence", "Google Workspace", "Microsoft 365"]),
    ("וידאו ושיחות",       ["Zoom", "Google Meet", "Webex", "Microsoft Teams"]),
    ("CRM ומכירות",        ["HubSpot CRM", "Salesforce", "Pipedrive", "Monday CRM"]),
    ("עיצוב ופרוטוטייפ",   ["Figma", "Sketch", "Adobe XD", "InVision"]),
    ("ניהול ידע",           ["Notion", "Confluence", "Coda", "GitBook"]),
    ("לוח לבן דיגיטלי",    ["Miro", "Mural", "FigJam", "Lucidboard"]),
]

MIN_MONTHLY_EACH = 1_500   # חיסכון חודשי מינימלי לכל כלי להצגה
MIN_CONFIDENCE   = 0.70


def check(df: pd.DataFrame) -> list[Finding]:
    """
    מוצא: שני כלים (או יותר) מאותה קבוצת פונקציונליות ששניהם פעילים.
    מחשב את עלות הכלי הקטן כ-amount_at_risk.

    דורש: tool, seats_paid, price_per_seat_ils, monthly_total
    """
    required = {"tool", "seats_paid", "price_per_seat_ils"}
    if not required.issubset(df.columns):
        return []

    # בנה dict: tool_name -> row
    tool_map = {row["tool"]: row for _, row in df.iterrows()}
    active_tools = set(tool_map.keys())

    findings = []
    reported_pairs = set()

    for group_name, tools_in_group in OVERLAP_GROUPS:
        present = [t for t in tools_in_group if t in active_tools]
        if len(present) < 2:
            continue

        # כל זוג בתוך הקבוצה
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                t1, t2 = present[i], present[j]
                pair_key = frozenset({t1, t2})
                if pair_key in reported_pairs:
                    continue
                reported_pairs.add(pair_key)

                r1 = tool_map[t1]
                r2 = tool_map[t2]

                cost1 = float(r1.get("monthly_total", r1["seats_paid"] * r1["price_per_seat_ils"]))
                cost2 = float(r2.get("monthly_total", r2["seats_paid"] * r2["price_per_seat_ils"]))

                # ה-amount_at_risk = עלות הכלי הקטן × 12
                smaller_cost = min(cost1, cost2)
                if smaller_cost < MIN_MONTHLY_EACH:
                    continue

                amount_at_risk = smaller_cost * 12
                cheaper_tool   = t1 if cost1 <= cost2 else t2

                findings.append(Finding(
                    rule_id        = RULE_ID,
                    title          = f"כפילות פונקציונלית — {t1} ו-{t2} ({group_name})",
                    amount_at_risk = amount_at_risk,
                    confidence     = MIN_CONFIDENCE,
                    evidence       = [r1.to_dict(), r2.to_dict()],
                    action         = (
                        f"{t1} ו-{t2} מבצעים את אותה מטרה ({group_name}). "
                        f"שקול לאחד תחת כלי אחד. "
                        f"ביטול {cheaper_tool} יחסוך ~₪{amount_at_risk:,.0f}/שנה."
                    ),
                    category       = CATEGORY,
                ))
    return findings
