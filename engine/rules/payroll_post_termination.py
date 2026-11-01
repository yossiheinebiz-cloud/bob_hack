# -*- coding: utf-8 -*-
"""engine/rules/payroll_post_termination.py — שכר אחרי סיום העסקה"""
import pandas as pd
from datetime import date
from engine.models import Finding

RULE_ID  = "PAYROLL_POST_TERMINATION"
CATEGORY = "payroll"


def check(payroll: pd.DataFrame, employees: pd.DataFrame) -> list[Finding]:
    """
    מוצא: עובדים שמקבלים שכר אחרי תאריך סיום ההעסקה.
    דורש:
      payroll:   employee_id, month, total
      employees: employee_id, end_date, status
    """
    req_pay = {"employee_id", "month", "total"}
    req_emp = {"employee_id", "end_date", "status"}
    if not req_pay.issubset(payroll.columns) or not req_emp.issubset(employees.columns):
        return []

    terminated = employees[
        (employees["status"] == "terminated") & (employees["end_date"].notna()) & (employees["end_date"] != "")
    ][["employee_id", "end_date"]].copy()

    if terminated.empty:
        return []

    merged = payroll.merge(terminated, on="employee_id", how="inner")
    merged["month_date"]  = pd.to_datetime(merged["month"]).dt.date
    merged["end_date_dt"] = pd.to_datetime(merged["end_date"]).dt.date
    overpaid = merged[merged["month_date"] > merged["end_date_dt"]]

    findings = []
    for emp_id, grp in overpaid.groupby("employee_id"):
        total_overpaid = float(grp["total"].sum())
        end_date       = grp["end_date"].iloc[0]
        months_count   = len(grp)
        findings.append(Finding(
            rule_id       = RULE_ID,
            title         = f"שכר אחרי סיום העסקה — {emp_id}",
            amount_at_risk= total_overpaid,
            confidence    = 1.0,
            evidence      = grp.to_dict("records"),
            action        = f"עובד {emp_id} סיים ב-{end_date}. שולם שכר {months_count} חודשים אחרי הסיום. בדוק ובקש החזר.",
            category      = CATEGORY,
        ))
    return findings
