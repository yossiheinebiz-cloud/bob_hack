# -*- coding: utf-8 -*-
"""
scripts/generate_data.py
Run: python scripts/generate_data.py
Output: data/synthetic/*.csv
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
OUT = Path("data/synthetic")
OUT.mkdir(parents=True, exist_ok=True)

# ─── עזרים ──────────────────────────────────────────────────────────────────

def rand_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))

def fmt(d: date) -> str:
    return d.strftime("%Y-%m-%d")

TODAY = date(2026, 11, 1)
YEAR_START = date(2026, 1, 1)

# ─── 1. EMPLOYEES ────────────────────────────────────────────────────────────
print("יוצר employees.csv...")

DEPARTMENTS = ["R&D", "Product", "Design", "Marketing", "Finance", "HR", "DevOps"]
ROLES = {
    "R&D":       [("Software Engineer", 28000), ("Senior Engineer", 38000), ("Tech Lead", 50000)],
    "Product":   [("Product Manager", 35000), ("Senior PM", 48000)],
    "Design":    [("Designer", 25000), ("Senior Designer", 34000)],
    "Marketing": [("Marketing Manager", 28000), ("Growth Hacker", 24000)],
    "Finance":   [("Finance Manager", 32000), ("Accountant", 24000)],
    "HR":        [("HR Manager", 28000), ("Recruiter", 22000)],
    "DevOps":    [("DevOps Engineer", 35000), ("SRE", 40000)],
}

FIRST_NAMES = ["דניאל", "שירה", "אבי", "מיכל", "יוסי", "רונית", "אמיר", "תמר",
               "גל", "נועה", "עידו", "מאיה", "איתמר", "ליאור", "הדר", "עומר"]
LAST_NAMES  = ["כהן", "לוי", "מזרחי", "פרץ", "ביטון", "אבולעפיה", "שפירא",
               "רוזנברג", "גולדברג", "אברהם", "חדד", "שמעון", "בן-דוד"]

employees = []
emp_id = 1000
for dept in DEPARTMENTS:
    n_employees = random.randint(6, 16)
    for _ in range(n_employees):
        role, base_salary = random.choice(ROLES[dept])
        start = rand_date(date(2020, 1, 1), date(2025, 6, 1))
        # 10% מהעובדים סיימו
        terminated = random.random() < 0.10
        end_date = rand_date(date(2025, 7, 1), date(2026, 8, 1)) if terminated else None

        employees.append({
            "employee_id":   f"EMP{emp_id:04d}",
            "department":    dept,
            "role":          role,
            "base_salary":   base_salary,
            "start_date":    fmt(start),
            "end_date":      fmt(end_date) if end_date else "",
            "bank_account":  f"IL{random.randint(10,99)}-{random.randint(100000,999999)}-{random.randint(100000000,999999999)}",
            "status":        "terminated" if terminated else "active",
        })
        emp_id += 1

# ── בעיה 4: עובד 47 — שכר 3 חודשים אחרי סיום ──
emp47_idx = 46 % len(employees)
employees[emp47_idx]["end_date"] = "2026-07-31"
employees[emp47_idx]["status"]   = "terminated"
employees[emp47_idx]["_planted"] = "PAYROLL_POST_TERMINATION"

# ── בעיה 5: שני עובדים עם אותו חשבון בנק ──
if len(employees) > 60:
    shared_ban = "IL12-123456-987654321"
    employees[55]["bank_account"] = shared_ban
    employees[62]["bank_account"] = shared_ban
    employees[55]["_planted"] = "PAYROLL_DUPLICATE_BANK"
    employees[62]["_planted"] = "PAYROLL_DUPLICATE_BANK"

df_emp = pd.DataFrame(employees)
df_emp.to_csv(OUT / "employees.csv", index=False, encoding="utf-8-sig")
print(f"  {len(df_emp)} עובדים")

# ─── 2. PAYROLL ──────────────────────────────────────────────────────────────
print("יוצר payroll.csv...")

payroll = []
MONTHS = [date(2026, m, 1) for m in range(1, 11)]  # ינואר–אוקטובר

for _, emp in df_emp.iterrows():
    emp_end = date.fromisoformat(emp["end_date"]) if emp["end_date"] else None
    for month in MONTHS:
        month_end = date(month.year, month.month, 28)
        # עצור שכר לעובדים שסיימו (אלא אם זה עובד 47 — שם שותלים בעיה)
        if emp_end and month > emp_end and emp.get("_planted") != "PAYROLL_POST_TERMINATION":
            continue
        # עבור עובד 47 — ממשיכים לשלם גם אחרי 31/07
        base = emp["base_salary"]
        overtime = 0

        # בעיה 5: קפיצת שעות נוספות לעובד ה-12 (index 12)
        if emp["employee_id"] == df_emp.iloc[12]["employee_id"] and month.month == 9:
            overtime = 4200  # קפיצה חדה בספטמבר

        payroll.append({
            "payroll_id":   f"PAY{len(payroll)+1:06d}",
            "employee_id":  emp["employee_id"],
            "month":        fmt(month),
            "base_salary":  base,
            "overtime":     overtime,
            "total":        base + overtime,
            "bank_account": emp["bank_account"],
        })

df_pay = pd.DataFrame(payroll)
df_pay.to_csv(OUT / "payroll.csv", index=False, encoding="utf-8-sig")
print(f"  {len(df_pay)} תלושים")

# ─── 3. INVOICES ─────────────────────────────────────────────────────────────
print("יוצר invoices.csv...")

VENDORS = [
    ("מילגם בע\"מ",         "IL-vendor-001"),
    ("מטריקס",             "IL-vendor-002"),
    ("AWS Israel",          "IL-vendor-003"),
    ("Google Cloud",        "IL-vendor-004"),
    ("רד-האט ישראל",       "IL-vendor-005"),
    ("טבעות תוכנה בע\"מ",  "IL-vendor-006"),
    ("Atlassian",           "IL-vendor-007"),
    ("Slack Technologies",  "IL-vendor-008"),
    ("HubSpot Inc",         "IL-vendor-009"),
    ("ClickUp",             "IL-vendor-010"),
    ("Zoom",                "IL-vendor-011"),
    ("Cloudflare",          "IL-vendor-012"),
]

invoices = []
_inv_counter = [4000]

def add_invoice(vendor_name, vendor_id, amount, inv_date, inv_id=None, note=""):
    _inv_counter[0] += 1
    invoices.append({
        "invoice_id":     f"INV{_inv_counter[0]:05d}" if not inv_id else inv_id,
        "vendor_name":    vendor_name,
        "vendor_id":      vendor_id,
        "amount":         amount,
        "currency":       "ILS",
        "invoice_date":   fmt(inv_date),
        "payment_date":   fmt(inv_date + timedelta(days=random.randint(5, 20))),
        "status":         "paid",
        "note":           note,
    })

# חשבוניות רגילות — ~480 שורות
for _ in range(480):
    vendor = random.choice(VENDORS)
    amount = round(random.uniform(800, 85000), -2)
    inv_date = rand_date(YEAR_START, TODAY)
    add_invoice(vendor[0], vendor[1], amount, inv_date)

# ── בעיה 1: DUP_INVOICE_EXACT — מילגם INV-4471 שולמה פעמיים ──
add_invoice("מילגם בע\"מ", "IL-vendor-001", 23400,
            date(2026, 3, 12), inv_id="INV04471", note="PLANTED:DUP_EXACT_1")
add_invoice("מילגם בע\"מ", "IL-vendor-001", 23400,
            date(2026, 3, 15), inv_id="INV04471", note="PLANTED:DUP_EXACT_2")

# ── בעיה 2: DUP_CROSS_CURRENCY — AWS אותה חשבונית בשתי מטבעות ──
add_invoice("AWS Israel", "IL-vendor-003", 44200,
            date(2026, 5, 1), inv_id="AWS-2026-0512", note="PLANTED:DUP_CURRENCY_ILS")
last = invoices[-1].copy()
last["currency"] = "USD"
last["amount"]   = 12000
last["note"]     = "PLANTED:DUP_CURRENCY_USD"
invoices.append(last)

# ── בעיה 3: INVOICE_SPLITTING — מטריקס 4 חשבוניות מתחת לסף 50K ──
for i, amount in enumerate([48500, 47200, 49100, 48800]):
    add_invoice("מטריקס", "IL-vendor-002", amount,
                date(2026, 6, i*5+1), note=f"PLANTED:SPLIT_{i+1}")

df_inv = pd.DataFrame(invoices)
df_inv.to_csv(OUT / "invoices.csv", index=False, encoding="utf-8-sig")
print(f"  {len(df_inv)} חשבוניות")

# ─── 4. LICENSES ─────────────────────────────────────────────────────────────
print("יוצר licenses.csv...")

n_employees_active = len(df_emp[df_emp["status"] == "active"])

TOOLS = [
    # (כלי, מחיר_לרישיון_חודשי, מס_רישיונות, מס_בשימוש_אמיתי, planted_issue)
    ("Figma",          140, 14,  6,  "LICENSE_UNUSED"),        # בעיה 6
    ("Slack Pro",       80, 87, 82,  "LICENSE_DEPARTED"),       # בעיה 7 — 5 עזבו
    ("GitHub Enterprise",120,87, 85, None),
    ("Jira",            90, 45, 43,  "LICENSE_DUPLICATE_FUNC"), # בעיה 8א
    ("Monday.com",     100, 42, 38,  "LICENSE_DUPLICATE_FUNC"), # בעיה 8ב
    ("Zoom",            70, 30, 28,  None),
    ("HubSpot CRM",    400, 12, 11,  "AUTO_RENEWAL_JUMP"),      # בעיה 9
    ("Notion",          60, 20, 18,  None),
    ("Datadog",        200,  8,  8,  None),
    ("1Password",       40, 87, 84,  None),
    ("Loom",            30, 15,  9,  None),
    ("Miro",            80, 10,  7,  None),
    ("Linear",          80, 45, 42,  None),
    ("Canva",           55, 12,  8,  None),
    ("Postman",         50, 20, 18,  None),
]

licenses = []
for tool, price, seats, used, issue in TOOLS:
    renewal = rand_date(TODAY, date(2027, 6, 1))
    prev_price = price if issue != "AUTO_RENEWAL_JUMP" else round(price / 1.32)
    licenses.append({
        "tool":                tool,
        "seats_paid":          seats,
        "seats_used_30d":      used,
        "price_per_seat_ils":  price,
        "monthly_total":       price * seats,
        "renewal_date":        fmt(renewal),
        "prev_year_price":     prev_price,
        "price_change_pct":    round((price - prev_price) / prev_price * 100, 1),
        "planted_issue":       issue or "",
    })

df_lic = pd.DataFrame(licenses)
df_lic.to_csv(OUT / "licenses.csv", index=False, encoding="utf-8-sig")
print(f"  {len(df_lic)} כלים")

# ─── 5. CLOUD COSTS ──────────────────────────────────────────────────────────
print("יוצר cloud_costs.csv...")

SERVICES = [
    ("ec2-prod",       "AWS", 18000),
    ("ec2-staging",    "AWS",  4400),   # ← זומבי — בעיה 10
    ("rds-prod",       "AWS",  8200),
    ("s3-storage",     "AWS",  1200),
    ("gke-prod",       "GCP",  6800),
    ("bigquery",       "GCP",  2100),
    ("cloudflare",     "CF",   1800),
    ("vercel",         "VC",    900),
]

cloud = []
for month_offset in range(24):  # 24 חודשים — מגיע עד נובמבר 2027
    month = date(2025, 5, 1) + timedelta(days=month_offset * 30)
    for service, provider, base_cost in SERVICES:
        # זומבי ec2-staging — תעבורה אפס מאוגוסט 2026 ואילך (3+ חודשים רצופים)
        if service == "ec2-staging":
            traffic_gb = 0 if month >= date(2026, 8, 1) else random.randint(500, 2000)
        else:
            traffic_gb = random.randint(1000, 50000)

        variance = random.uniform(0.85, 1.15)
        cloud.append({
            "month":       fmt(month),
            "service":     service,
            "provider":    provider,
            "cost_ils":    round(base_cost * variance, 0),
            "traffic_gb":  traffic_gb,
            "planted_issue": "CLOUD_ZOMBIE" if service == "ec2-staging" and month >= date(2026, 9, 1) else "",
        })

df_cloud = pd.DataFrame(cloud)
df_cloud.to_csv(OUT / "cloud_costs.csv", index=False, encoding="utf-8-sig")
print(f"  {len(df_cloud)} שורות ענן")

# ─── סיכום ───────────────────────────────────────────────────────────────────
print("\n✅ כל הקבצים נוצרו:")
for f in sorted(OUT.glob("*.csv")):
    df = pd.read_csv(f)
    print(f"  {f.name:<25} {len(df):>6} שורות")

print("\n🌱 בעיות שתולות:")
planted = [
    ("1", "DUP_INVOICE_EXACT",      "מילגם INV-4471 שולמה פעמיים",           "₪23,400"),
    ("2", "DUP_CROSS_CURRENCY",     "AWS אותה חשבונית ₪ ו-$",               "₪44,200"),
    ("3", "INVOICE_SPLITTING",      "מטריקס 4 חשבוניות מתחת לסף",           "₪193,600"),
    ("4", "PAYROLL_POST_TERMINATION","עובד 47 — שכר 3 חודשים אחרי סיום",    "₪28,500"),
    ("5", "PAYROLL_DUPLICATE_BANK", "שני עובדים אותו BAN",                   "בדיקה"),
    ("6", "LICENSE_UNUSED",         "Figma — 14 רישיונות, 6 בשימוש",        "₪19,600/שנה"),
    ("7", "LICENSE_DEPARTED",       "Slack — 5 עובדים שעזבו",               "₪3,600/שנה"),
    ("8", "LICENSE_DUPLICATE_FUNC", "Jira + Monday — כפולים",               "₪24,000/שנה"),
    ("9", "AUTO_RENEWAL_JUMP",      "HubSpot +32% בחידוש",                  "₪14,400/שנה"),
    ("10","CLOUD_ZOMBIE",           "ec2-staging — 45 יום ללא תעבורה",      "₪8,400/שנה"),
]
for num, rule, desc, amount in planted:
    print(f"  {num:>2}. {rule:<30} {desc:<45} {amount}")

total = 23400 + 44200 + 193600 + 28500 + 19600 + 3600 + 24000 + 14400 + 8400
print(f"\n💰 סה\"כ שתול: ₪{total:,}")
