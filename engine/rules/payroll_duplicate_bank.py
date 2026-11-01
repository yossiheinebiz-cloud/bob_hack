# -*- coding: utf-8 -*-
"""engine/rules/payroll_duplicate_bank.py — שני עובדים עם אותו חשבון בנק"""
import pandas as pd
from engine.models import Finding

RULE_ID  = "PAYROLL_DUPLICATE_BANK"
CATEGORY = "payroll"


def check(employees: pd.DataFrame, payroll: pd.DataFrame) -> list[Finding]:
    """
    מוצא: שני עובדים פעילים ששותפים לאותו מספר חשבון בנק — עשוי להצביע
    על עובד רפאים, טעות הזנה, או תשלום כפול.

    דורש:
      employees: employee_id, bank_account, status
      payroll:   employee_id, total, month
    """
    req_emp = {"employee_id", "bank_account", "status"}
    if not req_emp.issubset(employees.columns):
        return []

    active = employees[
        (employees["status"] == "active") &
        employees["bank_account"].notna() &
        (employees["bank_account"] != "")
    ].copy()

    dupes = active.groupby("bank_account").filter(lambda g: len(g) > 1)
    if dupes.empty:
        return []

    findings = []
    for ban, grp in dupes.groupby("bank_account"):
        emp_ids = grp["employee_id"].tolist()

        # חשב סכום שנתי ששולם לחשבון הכפול
        amount_at_risk = 0.0
        if not payroll.empty and "employee_id" in payroll.columns:
            relevant = payroll[payroll["employee_id"].isin(emp_ids)]
            amount_at_risk = float(relevant["total"].sum())

        # מסתיר את ה-BAN המלא בלוג (Privacy — Amendment 13)
        masked_ban = ban[:6] + "****" + ban[-4:] if len(ban) > 10 else "****"

        findings.append(Finding(
            rule_id        = RULE_ID,
            title          = f"חשבון בנק משותף — {len(emp_ids)} עובדים (BAN: {masked_ban})",
            amount_at_risk = amount_at_risk,
            confidence     = 0.95,
            evidence       = grp.to_dict("records"),
            action         = (
                f"עובדים {', '.join(emp_ids)} שותפים לחשבון בנק. "
                f"בדוק מול HR: האם מדובר בטעות הזנה, בן משפחה, או עובד רפאים."
            ),
            category       = CATEGORY,
        ))
    return findings
