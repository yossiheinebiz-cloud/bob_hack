# -*- coding: utf-8 -*-
"""engine/rules/__init__.py — רשימת כל הכללים"""
from engine.rules.dup_invoice_exact        import check as check_dup_exact
from engine.rules.dup_cross_currency       import check as check_dup_cross_currency
from engine.rules.invoice_splitting        import check as check_invoice_splitting
from engine.rules.license_unused           import check as check_license_unused
from engine.rules.license_departed         import check as check_license_departed
from engine.rules.license_duplicate_func   import check as check_license_dup_func
from engine.rules.auto_renewal_jump        import check as check_auto_renewal
from engine.rules.payroll_post_termination import check as check_payroll_post_term
from engine.rules.payroll_duplicate_bank   import check as check_payroll_dup_bank
from engine.rules.cloud_zombie             import check as check_cloud_zombie

ALL_SINGLE_TABLE_RULES = [
    # (שם, פונקציה, טבלה)
    ("DUP_INVOICE_EXACT",       check_dup_exact,           "invoices"),
    ("DUP_CROSS_CURRENCY",      check_dup_cross_currency,  "invoices"),
    ("INVOICE_SPLITTING",       check_invoice_splitting,   "invoices"),
    ("LICENSE_UNUSED",          check_license_unused,      "licenses"),
    ("LICENSE_DUPLICATE_FUNC",  check_license_dup_func,    "licenses"),
    ("AUTO_RENEWAL_JUMP",       check_auto_renewal,        "licenses"),
    ("CLOUD_ZOMBIE",            check_cloud_zombie,        "cloud_costs"),
]

ALL_MULTI_TABLE_RULES = [
    # (שם, פונקציה, [טבלות])
    ("PAYROLL_POST_TERMINATION", check_payroll_post_term, ["payroll", "employees"]),
    ("PAYROLL_DUPLICATE_BANK",   check_payroll_dup_bank,  ["employees", "payroll"]),
    ("LICENSE_DEPARTED",         check_license_departed,  ["licenses", "employees"]),
]
