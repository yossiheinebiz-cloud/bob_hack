# -*- coding: utf-8 -*-
"""
engine/tests/test_rules.py
Run: python -m pytest engine/tests/ -v
"""
import pytest
import pandas as pd
from datetime import date

# ── Rules under test ─────────────────────────────────────────────────────────
from engine.rules.dup_invoice_exact      import check as dup_exact
from engine.rules.dup_cross_currency     import check as dup_cross
from engine.rules.invoice_splitting      import check as inv_split
from engine.rules.license_unused         import check as lic_unused
from engine.rules.license_duplicate_func import check as lic_dup_func
from engine.rules.auto_renewal_jump      import check as auto_renewal
from engine.rules.payroll_post_termination import check as payroll_post_term
from engine.rules.payroll_duplicate_bank   import check as payroll_dup_bank
from engine.rules.cloud_zombie           import check as cloud_zombie
from engine.models import Finding


# ════════════════════════════════════════════════════════════════════════════════
# DUP_INVOICE_EXACT
# ════════════════════════════════════════════════════════════════════════════════

class TestDupInvoiceExact:
    def _df(self, rows):
        return pd.DataFrame(rows)

    def test_finds_exact_duplicate(self):
        df = self._df([
            {"invoice_id":"INV001","vendor_name":"ספק א","amount":10000,"invoice_date":"2026-01-10","status":"paid"},
            {"invoice_id":"INV001","vendor_name":"ספק א","amount":10000,"invoice_date":"2026-01-15","status":"paid"},
        ])
        findings = dup_exact(df)
        assert len(findings) == 1
        assert findings[0].amount_at_risk == 10000
        assert findings[0].confidence == 1.0
        assert findings[0].category == "duplicates"

    def test_ignores_cancelled(self):
        df = self._df([
            {"invoice_id":"INV002","vendor_name":"ספק ב","amount":5000,"invoice_date":"2026-02-01","status":"paid"},
            {"invoice_id":"INV002","vendor_name":"ספק ב","amount":5000,"invoice_date":"2026-02-05","status":"cancelled"},
        ])
        findings = dup_exact(df)
        assert len(findings) == 0

    def test_no_dupe_different_ids(self):
        df = self._df([
            {"invoice_id":"INV003","vendor_name":"ספק ג","amount":8000,"invoice_date":"2026-03-01","status":"paid"},
            {"invoice_id":"INV004","vendor_name":"ספק ג","amount":8000,"invoice_date":"2026-03-10","status":"paid"},
        ])
        assert dup_exact(df) == []

    def test_missing_columns_returns_empty(self):
        df = pd.DataFrame([{"foo": "bar"}])
        assert dup_exact(df) == []


# ════════════════════════════════════════════════════════════════════════════════
# DUP_CROSS_CURRENCY
# ════════════════════════════════════════════════════════════════════════════════

class TestDupCrossCurrency:
    def test_finds_cross_currency_dup(self):
        df = pd.DataFrame([
            {"invoice_id":"AWS-001","vendor_name":"AWS","amount":44200,"currency":"ILS","invoice_date":"2026-05-01","status":"paid"},
            {"invoice_id":"AWS-001","vendor_name":"AWS","amount":12000,"currency":"USD","invoice_date":"2026-05-01","status":"paid"},
        ])
        findings = dup_cross(df)
        assert len(findings) == 1
        assert findings[0].confidence == 0.85

    def test_ignores_very_different_amounts(self):
        df = pd.DataFrame([
            {"invoice_id":"INV-X","vendor_name":"ספק","amount":1000,"currency":"ILS","invoice_date":"2026-01-01","status":"paid"},
            {"invoice_id":"INV-X","vendor_name":"ספק","amount":50000,"currency":"USD","invoice_date":"2026-01-01","status":"paid"},
        ])
        # 50000 USD = 185,000 ILS — way more than 10% off from 1000 ILS
        assert dup_cross(df) == []

    def test_same_currency_not_cross(self):
        df = pd.DataFrame([
            {"invoice_id":"INV-Y","vendor_name":"ספק","amount":5000,"currency":"ILS","invoice_date":"2026-01-01","status":"paid"},
            {"invoice_id":"INV-Y","vendor_name":"ספק","amount":5000,"currency":"ILS","invoice_date":"2026-01-05","status":"paid"},
        ])
        assert dup_cross(df) == []


# ════════════════════════════════════════════════════════════════════════════════
# INVOICE_SPLITTING
# ════════════════════════════════════════════════════════════════════════════════

class TestInvoiceSplitting:
    def test_finds_split_invoices(self):
        rows = []
        for i, amt in enumerate([48500, 47200, 49100, 48800]):
            rows.append({
                "vendor_name": "מטריקס",
                "amount": amt,
                "invoice_date": f"2026-06-{i*5+1:02d}",
                "status": "paid",
                "invoice_id": f"INV{i}",
            })
        df = pd.DataFrame(rows)
        findings = inv_split(df)
        assert len(findings) >= 1
        assert findings[0].category == "duplicates"
        assert findings[0].amount_at_risk >= 100_000

    def test_no_split_single_invoice(self):
        df = pd.DataFrame([
            {"vendor_name":"ספק","amount":48000,"invoice_date":"2026-01-01","status":"paid","invoice_id":"X"},
        ])
        assert inv_split(df) == []

    def test_no_split_spread_over_long_period(self):
        rows = [
            {"vendor_name":"ספק","amount":49000,"invoice_date":"2026-01-01","status":"paid","invoice_id":"A"},
            {"vendor_name":"ספק","amount":49000,"invoice_date":"2026-06-01","status":"paid","invoice_id":"B"},
            {"vendor_name":"ספק","amount":49000,"invoice_date":"2026-12-01","status":"paid","invoice_id":"C"},
        ]
        df = pd.DataFrame(rows)
        # 6 months apart — should not trigger
        findings = inv_split(df)
        assert len(findings) == 0


# ════════════════════════════════════════════════════════════════════════════════
# LICENSE_UNUSED
# ════════════════════════════════════════════════════════════════════════════════

class TestLicenseUnused:
    def test_finds_unused_licenses(self):
        df = pd.DataFrame([{
            "tool": "Figma", "seats_paid": 14, "seats_used_30d": 6,
            "price_per_seat_ils": 140,
        }])
        findings = lic_unused(df)
        assert len(findings) == 1
        assert findings[0].amount_at_risk == 8 * 140 * 12

    def test_ignores_fully_used(self):
        df = pd.DataFrame([{
            "tool": "Slack", "seats_paid": 50, "seats_used_30d": 50,
            "price_per_seat_ils": 80,
        }])
        assert lic_unused(df) == []

    def test_ignores_tiny_saving(self):
        # 1 unused seat × ₪10/month × 12 = ₪120 — below MIN_ANNUAL_ILS
        df = pd.DataFrame([{
            "tool": "Tool", "seats_paid": 10, "seats_used_30d": 9,
            "price_per_seat_ils": 10,
        }])
        assert lic_unused(df) == []


# ════════════════════════════════════════════════════════════════════════════════
# LICENSE_DUPLICATE_FUNC
# ════════════════════════════════════════════════════════════════════════════════

class TestLicenseDuplicateFunc:
    def test_finds_jira_monday_overlap(self):
        df = pd.DataFrame([
            {"tool":"Jira",       "seats_paid":45,"price_per_seat_ils":90, "monthly_total":4050,"seats_used_30d":43},
            {"tool":"Monday.com", "seats_paid":42,"price_per_seat_ils":100,"monthly_total":4200,"seats_used_30d":38},
        ])
        findings = lic_dup_func(df)
        assert any("Jira" in f.title and "Monday" in f.title for f in findings)

    def test_single_tool_no_overlap(self):
        df = pd.DataFrame([
            {"tool":"Jira","seats_paid":45,"price_per_seat_ils":90,"monthly_total":4050,"seats_used_30d":43},
        ])
        assert lic_dup_func(df) == []


# ════════════════════════════════════════════════════════════════════════════════
# AUTO_RENEWAL_JUMP
# ════════════════════════════════════════════════════════════════════════════════

class TestAutoRenewalJump:
    def test_finds_price_jump(self):
        df = pd.DataFrame([{
            "tool": "HubSpot CRM", "price_per_seat_ils": 400,
            "prev_year_price": 303, "seats_paid": 12,
            "renewal_date": "2027-03-01",
        }])
        findings = auto_renewal(df)
        assert len(findings) == 1
        assert findings[0].confidence == 0.90
        assert findings[0].amount_at_risk > 0

    def test_ignores_small_jump(self):
        df = pd.DataFrame([{
            "tool": "Tool", "price_per_seat_ils": 101,
            "prev_year_price": 100, "seats_paid": 5,
            "renewal_date": "2027-01-01",
        }])
        # 1% jump — below MIN_JUMP_PCT
        assert auto_renewal(df) == []


# ════════════════════════════════════════════════════════════════════════════════
# PAYROLL_POST_TERMINATION
# ════════════════════════════════════════════════════════════════════════════════

class TestPayrollPostTermination:
    def _make_data(self, end_date: str, months_after: int):
        emp = pd.DataFrame([{
            "employee_id": "EMP001", "end_date": end_date, "status": "terminated"
        }])
        pay_rows = []
        for i in range(1, months_after + 1):
            pay_rows.append({
                "employee_id": "EMP001",
                "month": f"2026-{8+i:02d}-01",
                "total": 25000,
            })
        pay = pd.DataFrame(pay_rows)
        return pay, emp

    def test_finds_post_termination_salary(self):
        pay, emp = self._make_data("2026-07-31", 3)
        findings = payroll_post_term(pay, emp)
        assert len(findings) == 1
        assert findings[0].amount_at_risk == 75000
        assert findings[0].confidence == 1.0

    def test_no_finding_for_active_employee(self):
        emp = pd.DataFrame([{"employee_id":"EMP002","end_date":"","status":"active"}])
        pay = pd.DataFrame([{"employee_id":"EMP002","month":"2026-08-01","total":30000}])
        assert payroll_post_term(pay, emp) == []

    def test_no_finding_before_end_date(self):
        pay, emp = self._make_data("2026-11-30", 0)
        # No payroll rows after end date
        pay = pd.DataFrame([{"employee_id":"EMP001","month":"2026-10-01","total":25000}])
        assert payroll_post_term(pay, emp) == []


# ════════════════════════════════════════════════════════════════════════════════
# PAYROLL_DUPLICATE_BANK
# ════════════════════════════════════════════════════════════════════════════════

class TestPayrollDuplicateBank:
    def test_finds_shared_bank_account(self):
        emp = pd.DataFrame([
            {"employee_id":"EMP055","bank_account":"IL12-123456-9876","status":"active"},
            {"employee_id":"EMP062","bank_account":"IL12-123456-9876","status":"active"},
        ])
        pay = pd.DataFrame([
            {"employee_id":"EMP055","total":28000,"month":"2026-10-01"},
            {"employee_id":"EMP062","total":32000,"month":"2026-10-01"},
        ])
        findings = payroll_dup_bank(emp, pay)
        assert len(findings) == 1
        assert findings[0].amount_at_risk == 60000

    def test_ignores_terminated_employees(self):
        emp = pd.DataFrame([
            {"employee_id":"EMP001","bank_account":"IL99-111111-1111","status":"terminated"},
            {"employee_id":"EMP002","bank_account":"IL99-111111-1111","status":"active"},
        ])
        pay = pd.DataFrame(columns=["employee_id","total","month"])
        # Only one active — no dupe
        findings = payroll_dup_bank(emp, pay)
        assert len(findings) == 0

    def test_unique_banks_no_finding(self):
        emp = pd.DataFrame([
            {"employee_id":"EMP003","bank_account":"IL11-111111-1111","status":"active"},
            {"employee_id":"EMP004","bank_account":"IL22-222222-2222","status":"active"},
        ])
        pay = pd.DataFrame(columns=["employee_id","total","month"])
        assert payroll_dup_bank(emp, pay) == []


# ════════════════════════════════════════════════════════════════════════════════
# CLOUD_ZOMBIE
# ════════════════════════════════════════════════════════════════════════════════

class TestCloudZombie:
    def _make_cloud(self, service, months_zero, months_active=6):
        rows = []
        # Active months first
        for i in range(months_active):
            rows.append({"month": f"2025-{i+1:02d}-01", "service": service,
                         "provider":"AWS","cost_ils":4000,"traffic_gb":1000})
        # Zero-traffic months
        for i in range(months_zero):
            rows.append({"month": f"2026-{i+8:02d}-01", "service": service,
                         "provider":"AWS","cost_ils":4000,"traffic_gb":0})
        return pd.DataFrame(rows)

    def test_finds_zombie_server(self):
        df = self._make_cloud("ec2-staging", months_zero=4)
        findings = cloud_zombie(df)
        assert len(findings) == 1
        assert findings[0].category == "cloud"

    def test_no_finding_short_zero_period(self):
        # IDLE_MONTHS=2, so only 1 month of zero traffic must not trigger
        df = self._make_cloud("ec2-staging", months_zero=1)
        assert cloud_zombie(df) == []

    def test_no_finding_with_traffic(self):
        rows = [{"month":f"2026-{i:02d}-01","service":"ec2-prod",
                 "provider":"AWS","cost_ils":5000,"traffic_gb":2000}
                for i in range(1, 10)]
        df = pd.DataFrame(rows)
        assert cloud_zombie(df) == []
