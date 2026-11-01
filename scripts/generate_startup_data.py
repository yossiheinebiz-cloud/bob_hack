# -*- coding: utf-8 -*-
"""
scripts/generate_startup_data.py — synthetic spend dataset for "טכנוסיס בע״מ" (Series B, 112 people).

Run:  python scripts/generate_startup_data.py          (writes data/startup/, deterministic, seed 42)
      python scripts/generate_startup_data.py --no-png  (skip Playwright screenshots of receipts)

Single source of truth for the planted findings: design/v2/assets/demo-data.js (F-1001..F-1026).
ALL DATA IS SYNTHETIC. Vendors are real services / public companies, every amount, invoice,
employee, bank account and phone number is invented. Law/accounting/consulting firms are fictional.
"""
import csv, json, hashlib, math, random, sys
from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "startup"
R = random.Random(42)
FX = 3.70                       # DEMO.company.usdIls — used for all "annualized ₪" conversions
START, END = date(2024, 11, 1), date(2026, 10, 31)
MONTHS = [(2024 + (10 + i) // 12, (10 + i) % 12 + 1) for i in range(24)]
LAST12 = range(12, 24)          # 11/2025 .. 10/2026
D = date.fromisoformat


def ms(i): y, m = MONTHS[i]; return date(y, m, 1)
def me(i): y, m = MONTHS[i]; return date(y, m, monthrange(y, m)[1])
def dim(i): return me(i).day
def mi(d): return (d.year - 2024) * 12 + d.month - 11
def ym(i): y, m = MONTHS[i]; return f"{y}-{m:02d}"
def days(a, b):
    d = a
    while d <= b:
        yield d; d += timedelta(1)


def fx(d):  # mild drift around 3.70; full sine cycle over each 12 months -> 12m average ≈ 3.70
    return round(FX + 0.04 * math.sin(2 * math.pi * (mi(d) + d.day / 31) / 12), 4)


def vat_rate(d): return 0.17 if d < D("2025-01-01") else 0.18


def alloc_threshold(d):  # Israeli Tax Authority allocation-number threshold (pre-VAT)
    if d < D("2025-01-01"): return 25000
    if d < D("2026-01-01"): return 20000
    if d < D("2026-06-01"): return 10000
    return 5000


def biz(d):  # Israeli banking days: Sun-Thu
    while d.weekday() in (4, 5): d += timedelta(1)
    return d


def biz_back(d):
    while d.weekday() in (4, 5): d -= timedelta(1)
    return d


def sha(s): return hashlib.sha256(s.encode()).hexdigest()[:16]
def g(i, trend): return (1 + trend) ** ((i - 23) / 12)
def norm12(trend): return sum(g(i, trend) for i in LAST12)
def r2(x): return round(x + 1e-9, 2)


def hp_number(seed):  # 9-digit Israeli company number "51xxxxxxC" with ID check digit
    body = "51" + f"{seed:06d}"
    s = 0
    for k, ch in enumerate(body):
        v = int(ch) * (1 if k % 2 == 0 else 2)
        s += v if v < 10 else v - 9
    return body + str((10 - s % 10) % 10)


def write(name, rows, cols):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / name, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return len(rows)


GT, NOISE = [], []   # ground truth
def plant(fid, rule, kind, amount, files, note):
    GT.append(dict(finding_id=fid, rule_id=rule, kind=kind, expected_amount_ils=amount, files=files, how=note))


# ════════════════════════════ 1. EMPLOYEES (HiBob-like) ════════════════════════════
NAMES = [("נועה","noa"),("מיכל","michal"),("רון","ron"),("אורי","uri"),("שי","shai"),("יעל","yael"),("דנה","dana"),
 ("אבי","avi"),("תמר","tamar"),("ליאת","liat"),("עומר","omer"),("איתי","itai"),("נוי","noy"),("עידו","ido"),("שירה","shira"),
 ("גיא","guy"),("מאיה","maya"),("אלון","alon"),("רוני","roni"),("יונתן","yonatan"),("הילה","hila"),("עמית","amit"),("ליאור","lior"),
 ("טל","tal"),("אסף","asaf"),("ענבל","inbal"),("יואב","yoav"),("קרן","keren"),("ניר","nir"),("אורית","orit"),("רועי","roy"),
 ("שני","shani"),("אייל","eyal"),("מורן","moran"),("עדי","adi"),("נדב","nadav"),("רותם","rotem"),("אביטל","avital"),("בן","ben"),
 ("גל","gal"),("ירדן","yarden"),("עינב","einav"),("אריאל","ariel"),("לירון","liron"),("מתן","matan"),("סהר","sahar"),("חן","chen"),
 ("אלה","ella"),("דור","dor"),("נטע","neta"),("אופיר","ofir"),("רז","raz"),("שחר","shahar"),("יובל","yuval"),("אדם","adam"),
 ("רעות","reut"),("זיו","ziv"),("הדר","hadar"),("אלעד","elad"),("ספיר","sapir"),("עוז","oz"),("נמרוד","nimrod"),("מיה","mia"),
 ("אור","or"),("תומר","tomer"),("אליה","elia"),("ורד","vered"),("דן","dan")]
DEPTS = {"R&D": 61, "Product": 9, "Sales": 14, "Marketing": 7, "Customer Success": 9, "G&A": 12}
TITLES = {"R&D": ["Backend Engineer", "Frontend Engineer", "Full Stack Engineer", "Data Engineer", "QA Engineer", "DevOps Engineer", "ML Engineer", "Team Lead"],
          "Product": ["Product Manager", "Product Designer", "UX Researcher"],
          "Sales": ["Account Executive", "SDR", "Sales Engineer"],
          "Marketing": ["Content Manager", "Growth Marketer", "Product Marketing Manager"],
          "Customer Success": ["CSM", "Support Engineer", "Onboarding Specialist"],
          "G&A": ["Accountant", "HR Business Partner", "Office Manager", "Legal Counsel", "Recruiter"]}
HEADS = {  # id: (name, dept, title, start)
 1000: ("שי", "R&D", "CTO", "2018-03-01"), 1001: ("מיכל", "G&A", "CFO", "2020-06-01"), 1002: ("רון", "R&D", "DevOps Lead", "2019-02-03"),
 1003: ("אורי", "R&D", "Head of Data", "2019-09-01"), 1004: ("נועה", "G&A", "Operations Manager", "2021-01-10"),
 1005: ("יעל", "G&A", "Finance Manager", "2021-04-01"), 1006: ("דנה", "Sales", "VP Sales", "2020-11-01"), 1007: ("אבי", "G&A", "CEO", "2018-01-01"),
 1008: ("תמר", "Product", "VP Product", "2019-05-01"), 1009: ("ליאת", "Marketing", "VP Marketing", "2021-07-01"),
 1010: ("עומר", "Customer Success", "VP Customer Success", "2021-03-01")}
DEPT_HEAD = {"R&D": "EMP-1000", "G&A": "EMP-1007", "Sales": "EMP-1006", "Product": "EMP-1008", "Marketing": "EMP-1009", "Customer Success": "EMP-1010"}

EMP_DAN, EMP_POST, EMP_CAR, EMP_BANK_A, EMP_BANK_B = "EMP-1061", "EMP-1047", "EMP-1019", "EMP-1033", "EMP-1088"
END20 = ["2024-12-31", "2025-01-31", "2025-02-28", "2025-03-31", "2025-04-30", "2025-05-31", "2025-06-30", "2025-08-31", "2025-09-30",
         "2025-10-31", "2025-12-31", "2026-01-31", "2026-02-28", "2026-03-31", "2026-04-30", "2026-05-31", "2026-06-30", "2026-08-14",
         "2026-08-31", "2026-10-15"]
SEAT_DEP_ENDS = {"2025-12-31", "2026-01-31", "2026-02-28", "2026-03-31", "2026-04-30", "2026-05-31", "2026-08-14"}      # F-1015 (7)
PHONE_DEP_ENDS = {"2025-08-31", "2025-09-30", "2025-10-31", "2025-12-31", "2026-02-28", "2026-04-30", "2026-06-30", "2026-08-14", "2026-08-31"}  # F-1024 (9)
CAR_NOISE_END = "2025-05-31"
PRORATE_NOISE_END = "2026-10-15"

emps = {}
pool = [i for i in range(1011, 1095) if i not in (1019, 1033, 1047, 1061, 1088)]
dep_other = R.sample(pool, 20)
end_of = {1047: "2026-09-30", 1061: "2026-07-14", 1019: "2026-07-31"}
for k, eid in enumerate(dep_other): end_of[eid] = END20[k]
hire_dates = sorted(D("2024-11-10") + timedelta(R.randint(0, 690)) for _ in range(40))
for n in range(135):
    eid = 1000 + n
    if eid in HEADS:
        nm, dept, title, st = HEADS[eid]
    else:
        nm = "דן" if eid == 1061 else R.choice(NAMES[10:-1])[0]
        dept, title = None, None
        st = str(hire_dates[eid - 1095]) if eid >= 1095 else str(D("2016-03-01") + timedelta(R.randint(0, 3100)))
    emps[f"EMP-{eid}"] = dict(employee_id=f"EMP-{eid}", first_name=nm, department=dept, title=title, start_date=st,
                              end_date=end_of.get(eid, ""), n=eid)
# departments: departed R&D for the seat/key/payroll plants, others weighted; actives fill DEMO counts exactly
need = dict(DEPTS)
for eid, (_, dept, *_r) in HEADS.items(): need[dept] -= 1
for e in emps.values():
    if e["department"]: continue
    if e["end_date"]:
        if e["end_date"] in SEAT_DEP_ENDS or e["n"] in (1047, 1061):
            e["department"] = "R&D"
        elif e["n"] == 1019:
            e["department"] = "Sales"
        else:
            e["department"] = R.choice(["R&D", "R&D", "R&D", "Sales", "Customer Success", "Marketing", "G&A"])
active_ids = [e for e in emps.values() if not e["department"] and not e["end_date"]]
for fixed in ("EMP-1033", "EMP-1088"):
    emps[fixed]["department"] = "R&D"; need["R&D"] -= 1
active_ids = [e for e in active_ids if e["employee_id"] not in ("EMP-1033", "EMP-1088")]
slots = [d for d, c in need.items() for _ in range(c)]
R.shuffle(slots)
for e, d in zip(active_ids, slots): e["department"] = d
assert len(slots) == len(active_ids), (len(slots), len(active_ids))
for e in emps.values():
    if not e["title"]: e["title"] = R.choice(TITLES[e["department"]])
emps[EMP_DAN]["title"] = "Data Scientist"; emps[EMP_POST]["title"] = "QA Engineer"; emps[EMP_CAR]["title"] = "Sales Director"
for e in emps.values():
    e["manager_id"] = "" if e["employee_id"] == "EMP-1007" else (
        "EMP-1007" if int(e["employee_id"][4:]) in HEADS else DEPT_HEAD[e["department"]])
    e["location"] = "תל אביב"
    e["bank_account_hash"] = sha(f"leumi-{e['n']}-{R.randint(10000, 99999)}")
    e["employment_status"] = "terminated" if e["end_date"] else "active"
emps[EMP_BANK_B]["bank_account_hash"] = emps[EMP_BANK_A]["bank_account_hash"]          # F-1019
for e in R.sample([e for e in emps.values() if e["department"] == "R&D" and not e["end_date"] and e["n"] > 1011], 4): e["location"] = "חיפה"
for e in R.sample([e for e in emps.values() if e["department"] == "Sales" and not e["end_date"] and e["n"] > 1011], 2): e["location"] = "ניו יורק"
for e in R.sample([e for e in emps.values() if not e["end_date"] and e["n"] > 1011 and e["n"] not in (1033, 1088)], 8): e["employment_status"] = "leave"
car_noise = next(e for e in emps.values() if e["end_date"] == CAR_NOISE_END)
sales_active = [e for e in emps.values() if e["department"] == "Sales" and not e["end_date"] and e["n"] > 1011]
CAR_EMPS = [f"EMP-{i}" for i in (1000, 1001, 1006, 1007, 1008, 1010)] + [e["employee_id"] for e in sales_active[:3]] + [EMP_CAR, car_noise["employee_id"]]
used4 = set()
for e in emps.values():
    e["car_lease"] = e["employee_id"] in CAR_EMPS
    while True:
        l4 = R.randint(1000, 9999)
        if l4 not in used4: break
    used4.add(l4)
    e["phone_line_id"] = f"05{R.choice('0234')}-XXX-{l4}"
EMP = list(emps.values())
def edate(e, k): return D(e[k]) if e[k] else None
def active_on(e, d): return D(e["start_date"]) <= d and (not e["end_date"] or D(e["end_date"]) >= d)
seat_departed = [e for e in EMP if e["end_date"] in SEAT_DEP_ENDS]
phone_departed = [e for e in EMP if e["end_date"] in PHONE_DEP_ENDS]
prorate_noise = next(e for e in EMP if e["end_date"] == PRORATE_NOISE_END)
released_noise = next(e for e in EMP if e["end_date"] == "2026-06-30")
assert len(seat_departed) == 7 and len(phone_departed) == 9
assert sum(1 for e in EMP if not e["end_date"]) == 112 and sum(1 for e in EMP if e["end_date"]) == 23

# ════════════════════════════ 2. PAYROLL (Israeli payslip) ════════════════════════════
def bl_er(gr): a = min(gr, 7522); b = max(0, min(gr, 50695) - 7522); return a * .0451 + b * .076
def bl_ee(gr): a = min(gr, 7522); b = max(0, min(gr, 50695) - 7522); return a * .0427 + b * .1217
def tax(gr):
    t, lo = 0, 0
    for hi, rt in [(7010, .10), (10060, .14), (16150, .20), (22440, .31), (46690, .35), (60130, .47), (1e9, .50)]:
        if gr > lo: t += (min(gr, hi) - lo) * rt
        lo = hi
    return max(0, t - 2.25 * 242)
def er_cost(gr): return gr * (1 + .065 + .0833 + .075) + bl_er(gr)
def net_of(gr): return gr - tax(gr) - bl_ee(gr) - .06 * gr - .025 * min(gr, 15712)
def solve(f, target, lo=1000, hi=200000):
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < target else (lo, mid)
    return lo

BASE = {"R&D": 36000, "Product": 33000, "Sales": 24000, "Marketing": 25000, "Customer Success": 19000, "G&A": 22000}
EXEC = {1000: 68000, 1001: 60000, 1002: 47000, 1003: 46000, 1004: 30000, 1005: 32000, 1006: 50000, 1007: 74000, 1008: 52000, 1009: 44000, 1010: 40000}
for e in EMP:
    e["base0"] = EXEC.get(e["n"], BASE[e["department"]] * R.uniform(0.75, 1.3))
    e["ot"] = e["department"] in ("Customer Success", "G&A") and e["n"] not in EXEC
def raise_f(i): return 1.0 if ms(i).year == 2024 else (1.04 if ms(i).year == 2025 else 1.0816)
def pay_day(i): return biz_back(me(i))

def payroll_rows(scale):
    rows = []
    for i in range(24):
        for e in EMP:
            st, en = D(e["start_date"]), edate(e, "end_date")
            if st > me(i) or (en and en < ms(i) and not (e["employee_id"] == EMP_POST and i == 23)):
                continue
            a, b = max(st, ms(i)), min(en, me(i)) if en else me(i)
            frac = 1.0 if (e["employee_id"] == EMP_POST and i == 23) else ((b - a).days + 1) / dim(i)
            base = e["base0"] * scale * raise_f(i)
            if e.get("fixed_gross"): base = e["fixed_gross"]
            ot = R.choice([0, 0, 0, 450, 900, 1600]) if e["ot"] else 0
            com = round(base * R.uniform(0, .35), 0) if e["department"] == "Sales" and e["n"] not in (1006,) else 0
            gr = r2(base * frac + ot + com)
            pe, sv, kh, bl = r2(gr * .065), r2(gr * .0833), r2(gr * .075), r2(bl_er(gr))
            rows.append(dict(employee_id=e["employee_id"], period=ym(i), base_salary=r2(base * frac), overtime=ot, commission=com,
                             gross=gr, pension_employer=pe, severance_employer=sv, keren_hishtalmut_employer=kh,
                             bituach_leumi_employer=bl, total_employer_cost=r2(gr + pe + sv + kh + bl),
                             income_tax=r2(tax(gr)), bituach_leumi_employee=r2(bl_ee(gr)), pension_employee=r2(gr * .06),
                             keren_hishtalmut_employee=r2(.025 * min(gr, 15712)), net=r2(net_of(gr)),
                             payment_date=str(pay_day(i)), bank_account_hash=e["bank_account_hash"]))
    return rows

state = R.getstate()
scale = 1.0
for _ in range(3):
    R.setstate(state)
    tot = sum(r["total_employer_cost"] for r in payroll_rows(scale) if r["period"] >= "2025-11")
    scale *= 55_200_000 / tot
emps[EMP_POST]["fixed_gross"] = round(solve(er_cost, 31500), 2)        # F-1014: Oct-2026 employer cost 31,500
emps[EMP_BANK_B]["fixed_gross"] = round(solve(net_of, 22000), 2)       # F-1019: monthly net 22,000
emps[EMP_POST]["ot"] = emps[EMP_BANK_B]["ot"] = False
R.setstate(state)
PAYROLL = payroll_rows(scale)
R.seed(4242)
plant("F-1014", "PAYROLL_POST_TERMINATION", "recovery", 31500,
      {"employees.csv": [EMP_POST], "payroll.csv": [f"{EMP_POST}|2026-10"]},
      "end_date 2026-09-30, payslip period 2026-10 generated & paid (payment_date 2026-10-29). amount = total_employer_cost of that payslip.")
plant("F-1019", "PAYROLL_DUPLICATE_BANK", "review", 22000,
      {"employees.csv": [EMP_BANK_A, EMP_BANK_B], "payroll.csv": [f"{EMP_BANK_A}|2026-10", f"{EMP_BANK_B}|2026-10"]},
      "two active employees share one bank_account_hash. amount = Oct-2026 net paid to the second record (EMP-1088).")

# ════════════════════════════ 3. VENDORS ════════════════════════════
VENDORS, VBY = [], {}
def vend(key, name, cat, cur, method, annual, sched="m", n=1, trend=.08, noise=.06, owner=None, country=None,
         card=None, lines=None, prefix=None, auto_renew=True, contract_end="", small=None):
    vid = f"V-{len(VENDORS) + 1:03d}"
    country = country or ("IL" if cur == "ILS" else "US")
    owner = owner or {"cloud": "רון", "ai": "אורי", "saas": "נועה", "ap": "יעל", "office": "נועה", "finance": "מיכל",
                      "telecom": "נועה", "payroll": "יעל"}[cat]
    v = dict(key=key, vendor_id=vid, name=name, category=cat, country=country, billing_currency=cur, payment_method=method,
             owner=owner, hp_number=hp_number(len(VENDORS) * 7919 % 999999) if country == "IL" else "",
             card_descriptor=card or (name.upper()[:22] if method == "card" else ""), contract_end=contract_end,
             auto_renew=auto_renew, annual=annual, sched=sched, n=n, trend=trend, noise=noise,
             lines=lines or ["שירותים"], prefix=prefix or f"{len(VENDORS) + 1:02d}", small=small)
    VENDORS.append(v); VBY[key] = v
    return v

L = lambda *a: list(a)
# ── cloud (6.1M)
vend("aws", "Amazon Web Services EMEA SARL", "cloud", "USD", "bank_transfer", 5_340_000, "special", country="LU", prefix="EUINIL")
vend("datadog", "Datadog Inc", "cloud", "USD", "bank_transfer", 410_000, "special", trend=.22, contract_end="2027-02-28", prefix="DD-")
vend("mongodb", "MongoDB Atlas", "cloud", "USD", "card", 182_000, "special", trend=.12, card="MONGODB CLOUD", country="US")
vend("cloudflare", "Cloudflare", "cloud", "USD", "card", 48_000, noise=.03, card="CLOUDFLARE")
vend("sentry", "Sentry", "cloud", "USD", "card", 30_000, noise=.04, card="SENTRY.IO")
vend("pagerduty", "PagerDuty", "cloud", "USD", "card", 22_000, noise=0, card="PAGERDUTY INC")
vend("vercel", "Vercel", "cloud", "USD", "card", 14_000, noise=.05, card="VERCEL INC.")
vend("grafana", "Grafana Labs", "cloud", "USD", "card", 12_000, noise=.05, card="GRAFANA LABS")
vend("snowflake", "Snowflake", "cloud", "USD", "bank_transfer", 40_000, lines=L("Compute credits", "Storage"), prefix="SF-")
vend("jfrog", "JFrog", "cloud", "USD", "bank_transfer", 26_000, noise=0, lines=L("Artifactory Pro X"), prefix="JF-")
vend("docker", "Docker Inc", "cloud", "USD", "card", 6_000, noise=0, card="DOCKER INC")
vend("logzio", "Logz.io", "cloud", "USD", "bank_transfer", 36_000, noise=0, lines=L("Log Management — legacy plan"), country="IL", prefix="LZ-")
vend("gcp", "Google Cloud", "cloud", "USD", "bank_transfer", 20_000, lines=L("BigQuery analysis", "Cloud Storage"), country="IE", prefix="GC-")
# ── ai (1.9M)  API spend comes from ai_usage.csv
vend("openai", "OpenAI LLC", "ai", "USD", "bank_transfer", 0, "special", prefix="OAI-")
vend("anthropic", "Anthropic PBC", "ai", "USD", "bank_transfer", 0, "special", prefix="ANT-")
vend("cursor", "Cursor (Anysphere)", "ai", "USD", "card", 0, "special", card="CURSOR, AI POWERED IDE", contract_end="2026-11-30", owner="שי")
vend("copilot", "GitHub Copilot", "ai", "USD", "card", 0, "special", card="GITHUB COPILOT", owner="שי")
vend("chatgpt", "ChatGPT Team", "ai", "USD", "card", 16_000, noise=0, card="OPENAI *CHATGPT TEAM")
vend("claudeteam", "Claude Team", "ai", "USD", "card", 13_300, noise=0, card="ANTHROPIC CLAUDE TEAM")
vend("pinecone", "Pinecone", "ai", "USD", "card", 22_200, noise=.05, card="PINECONE SYSTEMS")
vend("hf", "Hugging Face", "ai", "USD", "card", 8_900, noise=0, card="HUGGINGFACE")
vend("otter", "Otter.ai", "ai", "USD", "card", 5_000, noise=0, card="OTTER.AI")
vend("perplexity", "Perplexity", "ai", "USD", "card", 8_000, noise=0, card="PERPLEXITY AI")
vend("midjourney", "Midjourney", "ai", "USD", "card", 4_000, noise=0, card="MIDJOURNEY INC")
vend("elevenlabs", "ElevenLabs", "ai", "USD", "card", 9_000, noise=0, card="ELEVENLABS.IO")
# ── saas (3.4M)
S = lambda key, name, ann, **k: vend(key, name, "saas", k.pop("cur", "USD"), k.pop("method", "card"), ann, **k)
S("salesforce", "Salesforce", 388_000, method="bank_transfer", sched="a:02-01", trend=.04, auto_renew=False, contract_end="2027-01-31", owner="דנה", lines=L("Sales Cloud Enterprise — 18 users, annual"), prefix="SFDC-")
S("gws", "Google Workspace", 246_000, method="bank_transfer", trend=.03, noise=.01, contract_end="2027-06-30", lines=L("Google Workspace Business Plus"), country="IE", prefix="GWS-")
S("hubspot", "HubSpot", 187_500, cur="ILS", method="bank_transfer", sched="special", contract_end="2027-09-30", owner="דנה", country="IE", prefix="HS-")
S("github", "GitHub Enterprise", 172_000, method="bank_transfer", sched="a:01-10", trend=.09, contract_end="2027-01-09", owner="שי", lines=L("GitHub Enterprise Cloud — annual", "Advanced Security", "Actions minutes"), prefix="GH-")
S("atlassian", "Atlassian", 121_000, method="bank_transfer", sched="a:04-01", trend=.06, contract_end="2027-03-31", owner="שי", lines=L("Jira Software Cloud Standard — annual", "Confluence Cloud Standard — annual"), country="AU", prefix="AT-")
S("slack", "Slack", 118_000, method="bank_transfer", sched="a:11-15", trend=.02, contract_end="2026-11-14", lines=L("Slack Business+ — annual"), prefix="SL-")
S("figma", "Figma", 0, sched="special", card="FIGMA", contract_end="2027-04-30")
S("monday", "monday.com", 0, sched="special", card="MONDAY.COM", country="IL", contract_end="2027-02-28", owner="דנה")
S("notion", "Notion Labs", 0, sched="special", card="NOTION LABS, INC.")
S("zoom", "Zoom", 35_000, noise=0, card="ZOOM.US 888-799-9666")
S("1password", "1Password", 39_000, noise=0, card="1PASSWORD", country="CA")
S("miro", "Miro", 13_000, noise=0, card="MIRO.COM")
S("loom", "Loom", 17_000, noise=0, card="LOOM SUBSCRIPTION")
S("canva", "Canva", 4_000, noise=0, card="CANVA* PRO", country="AU", owner="ליאת")
S("docusign", "DocuSign", 12_000, sched="a:06-01", trend=.05, card="DOCUSIGN INC")
S("intercom", "Intercom", 180_000, method="bank_transfer", trend=.12, lines=L("Intercom Advanced — seats", "Fin AI resolutions"), country="IE", prefix="IC-", owner="עומר")
S("gong", "Gong", 83_000, method="bank_transfer", sched="a:07-01", trend=.06, lines=L("Gong Foundation — 14 seats, annual"), owner="דנה", prefix="GONG-")
S("linkedin", "LinkedIn Sales Navigator", 25_000, noise=0, card="LINKEDIN SALES NAV", owner="דנה", country="IE")
S("zoominfo", "ZoomInfo", 70_000, method="bank_transfer", sched="a:09-01", trend=.05, lines=L("ZoomInfo SalesOS — annual"), owner="דנה", prefix="ZI-")
S("hibob", "HiBob", 50_000, method="bank_transfer", noise=.02, lines=L("Bob HRIS — per employee"), country="GB", prefix="BOB-")
vend("priority", "פריוריטי תוכנה", "saas", "ILS", "direct_debit", 48_000, noise=0, lines=L("Priority Cloud ERP — מנוי חודשי"), owner="יעל")
S("vanta", "Vanta", 45_000, method="bank_transfer", sched="a:03-01", lines=L("Vanta SOC2 + ISO27001 — annual"), prefix="VAN-")
S("jetbrains", "JetBrains", 20_000, sched="a:01-20", card="JETBRAINS AMERICAS", country="CZ")
S("postman", "Postman", 9_000, noise=0, card="POSTMAN INC")
S("mixpanel", "Mixpanel", 40_000, method="bank_transfer", lines=L("Mixpanel Growth — events"), prefix="MP-")
S("segment", "Twilio Segment", 75_000, method="bank_transfer", lines=L("Segment Team — MTU"), prefix="SEG-")
S("lucid", "Lucid", 6_000, noise=0, card="LUCID SOFTWARE")
S("grammarly", "Grammarly", 5_000, noise=0, card="GRAMMARLY")
S("calendly", "Calendly", 4_000, noise=0, card="CALENDLY")
S("webflow", "Webflow", 9_000, noise=0, card="WEBFLOW.COM", owner="ליאת")
S("semrush", "Semrush", 8_000, noise=0, card="SEMRUSH", owner="ליאת")
S("hotjar", "Hotjar", 6_000, noise=0, card="HOTJAR", country="MT", owner="ליאת")
S("adobe", "Adobe", 15_000, noise=0, card="ADOBE *CREATIVE CLD", country="IE", owner="ליאת")
S("zapier", "Zapier", 7_000, noise=0, card="ZAPIER.COM")
S("typeform", "Typeform", 3_000, noise=0, card="TYPEFORM", country="ES")
S("greenhouse", "Greenhouse", 60_000, method="bank_transfer", sched="a:08-01", lines=L("Greenhouse Recruiting — annual"), prefix="GHS-")
S("snyk", "Snyk", 50_000, method="bank_transfer", sched="a:12-01", lines=L("Snyk Team — annual"), country="GB", prefix="SNYK-")
S("sonar", "SonarCloud", 8_000, noise=0, card="SONARSOURCE", country="CH")
S("wiz", "Wiz", 180_000, method="bank_transfer", sched="a:06-15", trend=.15, lines=L("Wiz Cloud Security — annual"), prefix="WIZ-")
S("crowdstrike", "CrowdStrike", 80_000, method="bank_transfer", sched="a:03-15", lines=L("Falcon Pro — endpoints, annual"), prefix="CS-")
S("cato", "Cato Networks", 100_000, method="bank_transfer", noise=0, lines=L("Cato SASE — sites & users"), country="IL", prefix="CATO-")
S("launchdarkly", "LaunchDarkly", 60_000, method="bank_transfer", noise=.02, lines=L("LaunchDarkly Pro — MAU"), prefix="LD-")
S("retool", "Retool", 50_000, method="bank_transfer", sched="a:09-15", lines=L("Retool Business — annual"), prefix="RT-")
S("fivetran", "Fivetran", 90_000, method="bank_transfer", lines=L("Fivetran MAR"), prefix="FT-")
S("dbt", "dbt Cloud", 30_000, noise=0, card="DBT LABS")
S("auth0", "Auth0 (Okta)", 80_000, method="bank_transfer", noise=.02, lines=L("Auth0 B2B Professional — MAU"), prefix="A0-")
S("pendo", "Pendo", 70_000, method="bank_transfer", sched="a:05-01", lines=L("Pendo Core — annual"), prefix="PND-")
S("productboard", "Productboard", 35_000, noise=0, card="PRODUCTBOARD")
S("lattice", "Lattice", 40_000, method="bank_transfer", sched="a:02-15", lines=L("Lattice Performance — annual"), prefix="LAT-")
S("clari", "Clari", 110_000, method="bank_transfer", sched="a:11-01", lines=L("Clari Forecast — annual"), owner="דנה", prefix="CLR-")
S("outreach", "Outreach", 85_000, method="bank_transfer", sched="a:04-15", lines=L("Outreach Engage — annual"), owner="דנה", prefix="OUT-")
S("knowbe4", "KnowBe4", 15_000, sched="a:10-15", card="KNOWBE4")
S("wix", "Wix", 3_000, noise=0, card="WIX.COM", country="IL", owner="ליאת")
S("mailchimp", "Mailchimp", 9_000, noise=.05, card="MAILCHIMP", owner="ליאת")
S("vimeo", "Vimeo", 4_000, noise=0, card="VIMEO.COM", owner="ליאת")
S("dropbox", "Dropbox", 10_000, noise=0, card="DROPBOX")
S("airtable", "Airtable", 8_000, noise=0, card="AIRTABLE.COM")
S("whimsical", "Whimsical", 3_000, noise=0, card="WHIMSICAL")
S("teamviewer", "TeamViewer", 6_000, noise=0, card="TEAMVIEWER", country="DE")
S("descript", "Descript", 4_000, noise=0, card="DESCRIPT", owner="ליאת")
S("lusha", "Lusha", 25_000, method="bank_transfer", sched="a:03-01", lines=L("Lusha Pro — annual credits"), country="IL", prefix="LU-", owner="דנה")
S("similarweb", "Similarweb", 45_000, method="bank_transfer", sched="a:07-15", lines=L("Similarweb Digital Research — annual"), country="IL", prefix="SW-", owner="ליאת")
S("microsoft", "Microsoft 365", 6_000, noise=0, card="MSFT *M365 BUSINESS", country="IE")
S("apple", "Apple Developer", 400, sched="a:02-10", card="APPLE.COM/BILL", country="IE")
S("cloudinary", "Cloudinary", 6_000, noise=0, card="CLOUDINARY")
# ── office (2.6M)
O = lambda key, name, ann, **k: vend(key, name, "office", k.pop("cur", "ILS"), k.pop("method", "bank_transfer"), ann, **k)
O("rent", "מגדלי הים — ניהול ושכירות", 1_380_000, trend=.04, noise=0, lines=L("דמי שכירות — קומות 14-15", "דמי ניהול", "חניות (22)"), owner="מיכל", contract_end="2028-12-31", auto_renew=False)
O("albar", "אלבר ציי רכב", 0, sched="special", method="direct_debit")
O("paz", "פז חברת נפט", 0, sched="special", method="direct_debit")
O("iec", "חברת החשמל לישראל", 0, sched="special", method="direct_debit")
O("cleaning", "ברק-אור שירותי ניקיון", 140_000, noise=.03, lines=L("ניקיון משרדים — חודשי", "חומרי ניקיון"))
O("nespresso", "נספרסו ישראל", 36_000, noise=.15, lines=L("קפסולות Nespresso Professional", "חלב ומטבחון"))
O("shufersal", "שופרסל", 45_000, sched="small", method="card", card="שופרסל דיל", small=(8, 470))
O("wolt", "Wolt", 43_000, sched="small", method="card", card="WOLT", small=(12, 300))
O("pango", "פנגו", 30_000, sched="small", method="card", card="פנגו חניה", small=(150, 17))
O("gett", "Gett Business", 55_000, n=4, noise=.2, lines=L("נסיעות מונית עסקיות"))
O("officedepot", "אופיס דיפו", 14_000, sched="small", method="card", card="אופיס דיפו", small=(3, 390))
O("ikea", "איקאה", 9_000, sched="small", method="card", card="איקאה נתניה", small=(.5, 1500))
O("amazon", "Amazon", 20_000, sched="small", method="card", card="AMAZON MKTPL*", cur="USD", country="US", small=(6, 75))
O("aliexpress", "AliExpress", 5_000, sched="small", method="card", card="ALIEXPRESS", cur="USD", country="CN", small=(4, 28))
O("water", "מי אביבים", 6_000, sched="b", method="direct_debit", noise=.1, lines=L("מים וביוב — דו-חודשי"))
O("plants", "ירוק בעיר צמחייה", 9_000, noise=0, lines=L("אחזקת צמחייה משרדית"))
O("uber", "Uber", 8_000, sched="small", method="card", card="UBER *TRIP", cur="USD", country="US", small=(5, 22))
O("booking", "Booking.com", 12_000, sched="small", method="card", card="BOOKING.COM", cur="USD", country="NL", small=(1, 300))
O("post", "דואר ישראל", 3_000, sched="small", method="card", card="דואר ישראל", small=(3, 80))
O("superpharm", "סופר-פארם", 6_000, sched="small", method="card", card="סופר-פארם", small=(3, 165))
O("elal", "אל על", 25_000, sched="small", method="card", card="אל על נתיבי אויר", small=(.8, 2600))
O("courier", "ש.ל. שליחויות", 8_000, noise=.2, lines=L("שליחויות"))
O("bakery", "מאפיית השכונה", 6_000, sched="small", method="card", card="מאפיית השכונה", small=(4, 125))
O("events", "גובה הפקות אירועים", 60_000, sched="x:.25", noise=.3, lines=L("הפקת אירוע צוות", "קייטרינג", "הגברה ותאורה"))
O("catering", "מעדני גורמה קייטרינג", 30_000, n=2, noise=.25, lines=L("ארוחות צוות — ימי שני"))
O("shagrir", "שגריר שירותי רכב", 5_000, sched="x:.3", noise=.3, lines=L("גרירה ושירותי דרך"))
O("kravitz", "קרביץ", 8_000, n=1, noise=.3, lines=L("ציוד משרדי"))
# ── ap / professional services (1.2M) — fictional firms
A = lambda key, name, ann, **k: vend(key, name, "ap", k.pop("cur", "ILS"), "bank_transfer", ann, **k)
A("law", "שמיר-כהן עורכי דין", 360_000, n=3, noise=.35, owner="מיכל", lines=L("ייעוץ משפטי שוטף", "הסכמי לקוחות", "דיני עבודה", "קניין רוחני — רישום סימן מסחר"))
A("cpa", "ברגר-אלון ושות׳ רואי חשבון", 180_000, noise=.05, lines=L("הנהלת חשבונות ודיווחים", "ייעוץ מס שוטף"))
A("codeplus", "קוד-פלוס ייעוץ", 74_000, sched="special", owner="מיכל")
A("talent", "טאלנט-ברידג׳ השמה", 150_000, sched="x:.45", noise=.3, lines=L("דמי השמה — מהנדס/ת", "דמי השמה — Account Executive"))
A("pr", "מגפון יחסי ציבור", 96_000, noise=0, owner="ליאת", lines=L("ריטיינר יחסי ציבור חודשי"))
A("lingo", "לינגו-תרגומים", 18_000, sched="x:.4", noise=.4, lines=L("תרגום ולוקליזציה"))
A("studio", "סטודיו נגה עיצוב", 45_000, noise=.2, owner="ליאת", lines=L("עיצוב גרפי — קמפיין", "עיצוב מצגות"))
A("tax", "אופק ייעוץ מס", 60_000, sched="q", noise=.1, lines=L("ייעוץ מס — רבעוני", "דוחות 102/126"))
A("uslaw", "Harlow & Pierce LLP", 120_000, sched="x:.35", noise=.35, cur="USD", country="US", lines=L("US corporate counsel", "Delaware filings"), prefix="HP-")
A("pnina", "פנינה ייעוץ ארגוני", 40_000, sched="x:.3", noise=.3, lines=L("סדנת הנהלה", "ליווי ארגוני"))
A("cyber", "סייבר-שילד ייעוץ אבטחה", 55_000, sched="x:.17", noise=.2, lines=L("מבדק חדירות", "סקר סיכוני סייבר"))
# ── finance (0.7M)
vend("arnona", "עיריית תל אביב-יפו — ארנונה", "finance", "ILS", "direct_debit", 300_000, "b", trend=.03, noise=0, lines=L("ארנונה — דו-חודשי"))
vend("insurance", "מגן-על סוכנות לביטוח", "finance", "ILS", "bank_transfer", 150_000, "a:01-01", trend=.06, lines=L("ביטוח D&O — שנתי", "ביטוח סייבר — שנתי", "ביטוח צד ג׳ ומעבידים"), auto_renew=False)
vend("stripe", "Stripe", "finance", "USD", "bank_transfer", 130_000, trend=.3, noise=.08, lines=L("Stripe processing fees"), country="IE", prefix="ST-")
vend("registrar", "רשם החברות", "finance", "ILS", "bank_transfer", 1_500, "a:03-01", trend=0, lines=L("אגרה שנתית"))
vend("calfee", "כאל — דמי כרטיס", "finance", "ILS", "card", 3_000, noise=0, card="כאל דמי כרטיס")
# ── telecom (0.3M)
vend("partner", "פרטנר תקשורת", "telecom", "ILS", "direct_debit", 0, "special", contract_end="2027-08-31")
vend("bezeq", "בזק", "telecom", "ILS", "direct_debit", 60_000, noise=0, lines=L("סיב אופטי עסקי 1Gb", "קווי טלפון"))
vend("twilio", "Twilio", "telecom", "USD", "bank_transfer", 100_000, trend=.25, noise=.08, lines=L("Programmable SMS", "Voice minutes"), prefix="TW-", owner="רון")
vend("bezeqint", "בזק בינלאומי", "telecom", "ILS", "direct_debit", 24_000, noise=0, lines=L("גיבוי אינטרנט ו-IP קבוע"))
# ── payroll vendors
vend("hilan", "חילן", "payroll", "ILS", "direct_debit", 36_000, noise=.02, lines=L("עיבוד שכר — לפי תלוש"), owner="יעל")
vend("papaya", "Papaya Global", "payroll", "USD", "bank_transfer", 48_000, noise=.03, lines=L("EOR fees — US employees"), prefix="PG-", owner="יעל")
vend("deel", "Deel", "payroll", "USD", "bank_transfer", 30_000, noise=.15, lines=L("Contractor management"), prefix="DL-", owner="יעל")

# ════════════════════════════ 4. INVOICES / CARD / BANK — engine ════════════════════════════
INVOICES, LINES, CARD, BANK = [], [], [], []
ap_seq = [0]
RESERVED = {"2026-0412", "2026-0187", "2025-1187", "2025-1188"}
inv_seq = {}
def next_num(v, d):
    while True:
        inv_seq[v["key"]] = inv_seq.get(v["key"], R.randint(100, 300) if v["category"] == "ap" else R.randint(1000, 4000)) + R.randint(1, 9)
        k = inv_seq[v["key"]]
        num = f"{d.year}-{k:04d}" if v["category"] == "ap" else str(30000 + k)
        if num not in RESERVED: break
    if v["country"] == "IL":
        return num
    return f"{v['prefix']}{d.strftime('%y%m')}{k:05d}"

def due_of(v, d):
    if v["payment_method"] == "direct_debit": return d + timedelta(10)
    if v["country"] == "IL":
        return me(mi(d)) + timedelta(30) if mi(d) < 24 else d + timedelta(45)   # שוטף+30
    return d + timedelta(30)

def add_invoice(v, d, pre, lines=None, number=None, alloc="auto", paid=None, status=None, po=None, note="", double_pay_days=None):
    cur = v["billing_currency"]
    israeli = v["country"] == "IL" and cur == "ILS"
    vr = vat_rate(d) if (israeli and v["key"] not in ("arnona", "insurance", "registrar")) else 0.0
    pre = r2(pre)
    va = r2(pre * vr)
    if alloc == "auto":
        alloc = str(R.randint(100000000, 999999999)) if (israeli and vr and pre > alloc_threshold(d)) else ""
    due = due_of(v, d)
    paid_d = paid or biz(due - timedelta(R.randint(0, 6)))
    st = status or ("paid" if paid_d <= END else "open")
    ap_seq[0] += 1
    doc = f"AP-{d.year % 100}-{ap_seq[0]:06d}"
    ref = f"{'TRF' if v['payment_method'] == 'bank_transfer' else 'DD'}{R.randint(10_000_000, 99_999_999)}" if st == "paid" else ""
    row = dict(ap_doc_id=doc, invoice_number=number or next_num(v, d), vendor_id=v["vendor_id"], vendor_name=v["name"],
               doc_type="חשבונית מס" if israeli else "Invoice", issue_date=str(d), due_date=str(due), currency=cur,
               amount_before_vat=pre, vat_rate=vr, vat_amount=va, total=r2(pre + va), allocation_number=alloc,
               po_number=po if po is not None else (f"PO-{R.randint(2400, 2999)}" if R.random() < .45 else ""),
               status=st, paid_date=str(paid_d) if st == "paid" else "", payment_method=v["payment_method"],
               payment_ref=ref, notes=note)
    INVOICES.append(row)
    lines = lines or split_lines(v, pre)
    for k, (desc, q, up) in enumerate(lines, 1):
        LINES.append(dict(ap_doc_id=doc, line_no=k, description=desc, quantity=q, unit_price=up, amount=r2(q * up), currency=cur))
    if st == "paid":
        bank_pay(v, paid_d, row)
    return row

def split_lines(v, pre):
    k = min(len(v["lines"]), R.randint(1, 3))
    if k == 1: return [(v["lines"][0], 1, pre)]
    w = [R.uniform(.5, 1.5) for _ in range(k)]
    parts = [r2(pre * x / sum(w)) for x in w]
    parts[-1] = r2(pre - sum(parts[:-1]))
    return [(v["lines"][j], 1, parts[j]) for j in range(k)]

def bank_pay(v, d, inv, desc=None, amount=None, ref=None):
    usd = inv["currency"] == "USD"
    BANK.append(dict(account="USD" if usd else "ILS", date=d, value_date=d,
                     description=desc or (f"{'הוראת קבע' if v['payment_method'] == 'direct_debit' else 'העברה מקוונת'} - {v['name']}"
                                          if not usd else f"SWIFT OUT - {v['name']}"),
                     reference=ref or inv["payment_ref"], debit=amount if amount is not None else inv["total"], credit=0.0))

CARDS = {"cloud": ("4417", "EMP-1002"), "ai": ("2290", "EMP-1000"), "saas": ("8812", "EMP-1004"), "office": ("8812", "EMP-1004"),
         "finance": ("3306", "EMP-1001"), "telecom": ("4417", "EMP-1002")}
OWNER_CARD = {"ליאת": ("5530", "EMP-1009"), "דנה": ("7781", "EMP-1006"), "שי": ("2290", "EMP-1000")}
MCC = {"cloud": "שירותי מחשוב", "ai": "שירותי מחשוב", "saas": "תוכנה", "office": "שונות", "finance": "שירותים פיננסיים", "telecom": "תקשורת"}

def add_card(v, d, amount, cur=None, holder=None, kind="רגילה"):
    cur = cur or v["billing_currency"]
    last4, emp = holder or OWNER_CARD.get(v["owner"]) or CARDS[v["category"]]
    if cur == "USD":
        orig = r2(amount); ch = r2(orig * fx(d)); fee = r2(ch * .025)
    else:
        orig = ch = r2(amount); fee = 0.0
    CARD.append(dict(card_last4=last4, cardholder_employee_id=emp, transaction_date=str(d), posting_date=str(d + timedelta(R.randint(1, 3))),
                     billing_date=str(date(d.year + d.month // 12, d.month % 12 + 1, 10)), merchant=v["card_descriptor"],
                     merchant_category=MCC[v["category"]], merchant_country=v["country"], original_amount=orig, original_currency=cur,
                     charged_ils=ch, fx_fee_ils=fee, transaction_type=kind, voucher=str(R.randint(10_000_000, 99_999_999))))
    return CARD[-1]

def amt_noise(v): return 1 + R.uniform(-v["noise"], v["noise"]) if v["noise"] else 1.0

def generic(v):
    A_, t, sch = v["annual"], v["trend"], v["sched"]
    usd = v["billing_currency"] == "USD"
    def emit(d, ils):
        amt = ils / FX if usd else ils
        if v["payment_method"] == "card":
            add_card(v, d, amt)
        else:
            n = v["n"]
            ws = [R.uniform(.6, 1.4) for _ in range(n)]
            for j in range(n):
                part = amt * ws[j] / sum(ws)
                if v["category"] == "ap" and not usd and 17000 <= part < 20000: part *= .86   # keep off the approval-threshold band
                dd = min(d + timedelta(int(j * 28 / n) + R.randint(0, 3)), me(mi(d)))
                add_invoice(v, dd, part)
    day = 1 + (int(v["vendor_id"][2:]) * 7) % 27
    if sch == "m":
        for i in range(24): emit(date(*MONTHS[i], min(day, dim(i))), A_ * g(i, t) / norm12(t) * amt_noise(v))
    elif sch in ("b", "q"):
        step = 2 if sch == "b" else 3
        for i in range(24):
            if MONTHS[i][1] % step == 1: emit(date(*MONTHS[i], min(day, 28)), A_ * step * g(i, t) / norm12(t) * amt_noise(v))
    elif sch.startswith("a:"):
        mm, dd = map(int, sch[2:].split("-"))
        idx = [i for i in range(24) if MONTHS[i][1] == mm]
        last = max(idx)
        for i in idx: emit(date(*MONTHS[i], dd), A_ * (1 + t) ** ((i - last) / 12))
    elif sch.startswith("x:"):
        p = float(sch[2:])
        for i in range(24):
            if R.random() < p: emit(date(*MONTHS[i], R.randint(1, 26)), A_ / 12 / p * g(i, t) / norm12(t) * 12 * amt_noise(v) / 1.0)
    elif sch == "small":
        per, avg = v["small"]
        tot_target = A_ * g(0, 0)  # flat
        cnt = [max(0, int(per + R.uniform(-.5, .5) * per + (1 if R.random() < per % 1 else 0))) for _ in range(24)]
        holders = SMALL_HOLDERS
        usd_ = v["billing_currency"] == "USD"
        k = A_ / (sum(cnt[12:]) * avg) if sum(cnt[12:]) else 0
        for i in range(24):
            for _ in range(cnt[i]):
                d = date(*MONTHS[i], R.randint(1, dim(i)))
                h = R.choice(holders)
                if not active_on(emps[h[1]], d): h = CARDS["office"]
                a = avg * k * R.uniform(.4, 1.6)
                add_card(v, d, a / FX if usd_ else a, holder=h)

SMALL_HOLDERS = [CARDS["office"]] + [(str(1100 + k * 731 % 8899), e["employee_id"]) for k, e in
                 enumerate(R.sample([e for e in EMP if not e["end_date"] and e["department"] in ("Sales", "Customer Success", "Marketing", "G&A")], 10))]

# ════════════════════════════ 5. AWS CUR (daily) ════════════════════════════
CUR = []
REGION = "eu-central-1"
def cur(d, prod, ut, op, rid, amt, unit, rate, cost, term="OnDemand", ltype="Usage", env="", team="", owner="", cluster="", src=""):
    CUR.append(dict(bill_billing_period_start_date=f"{d.year}-{d.month:02d}-01T00:00:00Z", line_item_usage_start_date=f"{d}T00:00:00Z",
                    line_item_usage_end_date=f"{d + timedelta(1)}T00:00:00Z", line_item_line_item_type=ltype, line_item_product_code=prod,
                    product_region_code=REGION, line_item_usage_type=ut, line_item_operation=op, line_item_resource_id=rid,
                    line_item_usage_amount=round(amt, 6), pricing_unit=unit, line_item_unblended_rate=round(rate, 6),
                    line_item_unblended_cost=round(cost, 6), pricing_term=term, line_item_currency_code="USD",
                    resource_tags_user_env=env, resource_tags_user_team=team, resource_tags_user_owner=owner,
                    resource_tags_user_cluster=cluster, resource_tags_user_source_instance=src))

def iid(): return "i-0" + "".join(R.choice("0123456789abcdef") for _ in range(16))
RON, URI = "ron@technosis.io", "uri@technosis.io"
# F-1002 prod On-Demand nodes: last-12m cost = 172000 / (0.75 * 0.28 * 3.70)
OD_TARGET_DAY = 172000 / (0.75 * 0.28 * FX) / 365
od_nodes = [("r6i.12xlarge", 3.624)] * 3 + [("m6i.12xlarge", 2.765)] * 3 + [("c6i.12xlarge", 2.328)] * 2 + [("m6i.4xlarge", .922)]
k_od = OD_TARGET_DAY / (sum(r for _, r in od_nodes) * 24)
od_nodes = [(t, r * k_od, iid()) for t, r in od_nodes]
# Savings-Plan-covered nodes: so that On-Demand = 68% of all compute
DEV_RATE = 63000 / (98 / 168) / FX / 365 / 14 / 24                          # F-1006: 14 dev instances
od_compute_year = OD_TARGET_DAY * 365 + DEV_RATE * 24 * 14 * 365 + DEV_RATE * 24 * 3 * 365
sp_day = od_compute_year * 32 / 68 / 365
sp_nodes = [("m6i.12xlarge", sp_day / 7 / 24, iid()) for _ in range(7)]
dev_nodes = [iid() for _ in range(14)]
stg_nodes = [iid() for _ in range(3)]
kafka_vols = [("vol-0" + sha(f"kv{k}")[:16], sp_nodes[k][2]) for k in range(3)]
nat_ingest = "nat-0ingest7c1e5a9d2f40"
nat_prod = "nat-0prod41aa0c9be3d17"
STG_DAY = 96000 / FX / 365          # F-1003: staging-old run-rate per day (USD)
ZOMBIE_FROM = D("2026-09-15")
# F-1013 orphans: 38 volumes + 214 snapshots of terminated instances, Oct-2026 cost = 31200/3.7/12
dead = [iid() for _ in range(19)]
orph_vols = [("vol-0" + sha(f"ov{k}")[:16], R.randint(60, 400), dead[k % 19]) for k in range(38)]
orph_snaps = [("snap-0" + sha(f"os{k}")[:16], R.randint(8, 80), dead[k % 19]) for k in range(214)]
oct_raw = sum(s for _, s, _ in orph_vols) * .0952 + sum(s for _, s, _ in orph_snaps) * .054
k_orph = (31200 / FX / 12) / oct_raw
ORPH_FROM = D("2026-09-01")
AWS_TOTAL = 5_340_000 / FX
FILL_SVC = [  # (product, usage_type, op, rid, unit, rate, weight, instance_based, env, team)
 ("AmazonRDS", "EUC1-Multi-AZUsage:db.r6g.4xlarge", "CreateDBInstance:0016", "arn:aws:rds:eu-central-1:4412:db:prod-main", "Hrs", 3.88, .17, True, "prod", "platform"),
 ("AmazonRDS", "EUC1-RDS:Multi-AZ-GP3-Storage", "CreateDBInstance:0016", "arn:aws:rds:eu-central-1:4412:db:prod-main#storage", "GB-Mo", .27, .04, False, "prod", "platform"),
 ("AmazonS3", "EUC1-TimedStorage-ByteHrs", "StandardStorage", "technosis-data-lake", "GB-Mo", .0245, .08, False, "prod", "data"),
 ("AmazonS3", "EUC1-Requests-Tier1", "PutObject", "technosis-data-lake", "Requests", .0000054, .03, False, "prod", "data"),
 ("AmazonCloudFront", "EU-DataTransfer-Out-Bytes", "GET", "E2TQ9V1ABCXYZ", "GB", .085, .05, False, "prod", "web"),
 ("AWSELB", "EUC1-LoadBalancerUsage", "LoadBalancing:Application", "app/prod-public/8f1c2d", "Hrs", .027, .01, False, "prod", "platform"),
 ("AWSELB", "EUC1-LCUUsage", "LoadBalancing:Application", "app/prod-public/8f1c2d", "LCU-Hrs", .0096, .03, False, "prod", "platform"),
 ("AmazonEC2", "EUC1-NatGateway-Bytes", "NatGateway", nat_prod, "GB", .052, .03, False, "prod", "platform"),
 ("AWSDataTransfer", "EUC1-DataTransfer-Out-Bytes", "", "", "GB", .09, .06, False, "prod", "platform"),
 ("AmazonElastiCache", "EUC1-NodeUsage:cache.r6g.xlarge", "CreateCacheCluster:0002", "prod-redis", "Hrs", .52, .05, True, "prod", "platform"),
 ("AmazonMSK", "EUC1-Kafka.m5.2xlarge", "RunBroker", "arn:aws:kafka:eu-central-1:4412:cluster/prod-events", "Hrs", .91, .07, True, "prod", "data"),
 ("AmazonCloudWatch", "EUC1-DataProcessing-Bytes", "PutLogEvents", "", "GB", .63, .05, False, "prod", "platform"),
 ("AmazonDynamoDB", "EUC1-ReadRequestUnits", "PayPerRequestThroughput", "sessions", "ReadRequestUnits", .000000305, .04, False, "prod", "backend"),
 ("AWSLambda", "EUC1-Lambda-GB-Second", "Invoke", "", "Lambda-GB-Second", .0000166667, .02, False, "prod", "backend"),
 ("AmazonES", "EUC1-ESInstance:r6g.2xlarge.search", "ESDomain", "prod-search", "Hrs", .98, .07, True, "prod", "backend"),
 ("AmazonECR", "EUC1-TimedStorage-ByteHrs", "", "technosis/app", "GB-Mo", .10, .01, False, "prod", "platform"),
 ("AmazonEC2", "EUC1-EBS:VolumeUsage.gp3", "CreateVolume-Gp3", "kafka", "GB-Mo", .0952, .03, False, "prod", "data"),
]

def nat_ingest_gb_month(i): return 28000 if ms(i) >= D("2026-08-01") else 9000
for i in range(24):
    total_m = AWS_TOTAL * g(i, .18) / norm12(.18)
    dm = dim(i)
    planted = (OD_TARGET_DAY + sp_day + DEV_RATE * 24 * 14 + STG_DAY) * dm + nat_ingest_gb_month(i) * .052 + .052 * 24 * dm
    if ms(i) >= ORPH_FROM: planted += oct_raw * k_orph
    fill = total_m - planted
    support = fill * .07
    inst = {}
    for s in FILL_SVC:
        if s[7]: inst[s[3]] = max(1, round(fill * s[6] / dm / (s[5] * 24)))
    inst_cost = sum(inst[s[3]] * s[5] * 24 * dm for s in FILL_SVC if s[7])
    var_w = sum(s[6] for s in FILL_SVC if not s[7])
    var_total = fill - support - inst_cost
    cur(ms(i), "AWSSupportBusiness", "Dollar", "", "", support, "Dollar", 1, support, ltype="Fee")
    for d in days(ms(i), me(i)):
        for t, r, rid in od_nodes:
            cur(d, "AmazonEC2", f"EUC1-BoxUsage:{t}", "RunInstances", rid, 24, "Hrs", r, r * 24, env="prod", team="platform", owner=RON, cluster="prod-main")
        for t, r, rid in sp_nodes:
            cur(d, "AmazonEC2", f"EUC1-BoxUsage:{t}", "RunInstances", rid, 24, "Hrs", r, r * 24, term="SavingsPlan", ltype="SavingsPlanCoveredUsage", env="prod", team="platform", owner=RON, cluster="prod-main")
        for rid in dev_nodes:
            cur(d, "AmazonEC2", "EUC1-BoxUsage:m6i.xlarge", "RunInstances", rid, 24, "Hrs", DEV_RATE, DEV_RATE * 24, env="dev", team="rnd", owner=RON)
        # staging-old (F-1003): nodes + EKS + NAT + ALB + EBS + logs; ALB LCU = 0 since 15/09/2026
        zombie = d >= ZOMBIE_FROM
        c_nodes = DEV_RATE * 24
        for rid in stg_nodes:
            cur(d, "AmazonEC2", "EUC1-BoxUsage:m6i.xlarge", "RunInstances", rid, 24, "Hrs", DEV_RATE, c_nodes, env="staging", team="platform", owner=RON, cluster="staging-old")
        ebs = 1500 / dm * .0952
        fixed = 3 * c_nodes + 2.4 + .052 * 24 + .027 * 24 + ebs + 3.15
        lcu = 0 if zombie else R.uniform(25, 40)
        cur(d, "AmazonEKS", "EUC1-AmazonEKS-Hours:perCluster", "CreateOperation", "arn:aws:eks:eu-central-1:4412:cluster/staging-old", 24, "Hrs", .10, 2.4, env="staging", team="platform", owner=RON, cluster="staging-old")
        cur(d, "AmazonEC2", "EUC1-NatGateway-Hours", "NatGateway", "nat-0stg9a1be55c0d21f7", 24, "Hrs", .052, .052 * 24, env="staging", team="platform", owner=RON, cluster="staging-old")
        nat_gb = (STG_DAY - fixed) / .052
        cur(d, "AmazonEC2", "EUC1-NatGateway-Bytes", "NatGateway", "nat-0stg9a1be55c0d21f7", nat_gb, "GB", .052, nat_gb * .052, env="staging", team="platform", owner=RON, cluster="staging-old")
        cur(d, "AWSELB", "EUC1-LoadBalancerUsage", "LoadBalancing:Application", "app/staging-old/3e9d0a", 24, "Hrs", .027, .027 * 24, env="staging", team="platform", owner=RON, cluster="staging-old")
        cur(d, "AWSELB", "EUC1-LCUUsage", "LoadBalancing:Application", "app/staging-old/3e9d0a", lcu, "LCU-Hrs", .0096, lcu * .0096, env="staging", team="platform", owner=RON, cluster="staging-old")
        cur(d, "AmazonEC2", "EUC1-EBS:VolumeUsage.gp3", "CreateVolume-Gp3", "vol-0stagingold5d2e7f", 1500 / dm, "GB-Mo", .0952, ebs, env="staging", team="platform", owner=RON, cluster="staging-old", src=stg_nodes[0])
        cur(d, "AmazonCloudWatch", "EUC1-DataProcessing-Bytes", "PutLogEvents", "/aws/eks/staging-old", 5, "GB", .63, 3.15, env="staging", team="platform", owner=RON, cluster="staging-old")
        # F-1010 NAT ingest
        gb = nat_ingest_gb_month(i) / dm
        cur(d, "AmazonEC2", "EUC1-NatGateway-Hours", "NatGateway", nat_ingest, 24, "Hrs", .052, .052 * 24, env="prod", team="data", owner=URI)
        cur(d, "AmazonEC2", "EUC1-NatGateway-Bytes", "NatGateway", nat_ingest, gb, "GB", .052, gb * .052, env="prod", team="data", owner=URI)
        # F-1013 orphans
        if d >= ORPH_FROM:
            for rid, size, src in orph_vols:
                u = size * k_orph / dm
                cur(d, "AmazonEC2", "EUC1-EBS:VolumeUsage.gp3", "CreateVolume-Gp3", rid, u, "GB-Mo", .0952, u * .0952, src=src)
            for rid, size, src in orph_snaps:
                u = size * k_orph / dm
                cur(d, "AmazonEC2", "EUC1-EBS:SnapshotUsage", "CreateSnapshot", rid, u, "GB-Mo", .054, u * .054, src=src)
        # fill services
        for prod, ut, op, rid, unit, rate, w, ib, env, team in FILL_SVC:
            if ib:
                n = inst[rid]
                cur(d, prod, ut, op, rid, n * 24, unit, rate, n * 24 * rate, env=env, team=team, owner=RON)
            elif rid == "kafka":
                for vid, src in kafka_vols:
                    c = var_total * w / var_w / dm / 3 * R.uniform(.97, 1.03)
                    cur(d, prod, ut, op, vid, c / rate, unit, rate, c, env=env, team=team, owner=RON, src=src)
            else:
                c = var_total * w / var_w / dm * R.uniform(.9, 1.1)
                cur(d, prod, ut, op, rid, c / rate, unit, rate, c, env=env, team=team, owner=RON)
plant("F-1002", "CLOUD_NO_COMMITMENT", "recurring", 172000, {"aws_cur.csv": [n[2] for n in od_nodes]},
      "prod EC2 BoxUsage with pricing_term=OnDemand (9 nodes, flat for 24 months) ≈ 68% of all EC2 compute. "
      "amount = last-12m prod On-Demand compute USD × 0.75 (cover 75% of base) × 0.28 (1y no-upfront Compute SP discount) × 3.70.")
plant("F-1003", "CLOUD_ZOMBIE", "recurring", 96000, {"aws_cur.csv": ["resource_tags_user_cluster=staging-old"]},
      "all resources tagged cluster=staging-old; LCUUsage usage_amount = 0 from 2026-09-15. amount = avg daily cost 15/09–31/10 × 365 × 3.70.")
plant("F-1006", "CLOUD_DEV_ALWAYS_ON", "recurring", 63000, {"aws_cur.csv": dev_nodes},
      "14 env=dev instances bill 24h every day incl. Fri/Sat. amount = last-12m dev BoxUsage USD × 98/168 off-hours share (21:00–07:00 Sun–Thu + weekend) × 3.70.")
plant("F-1010", "CLOUD_EGRESS_SPIKE", "recurring", 44000, {"aws_cur.csv": [nat_ingest]},
      "NatGateway-Bytes on the ingest NAT: 9,000 GB/month until 07/2026, 28,000 GB/month from 08/2026. amount = (avg monthly Aug–Oct 2026 − avg monthly Jan–Jul 2026) × 12 × 3.70.")
plant("F-1013", "CLOUD_ORPHAN_STORAGE", "recurring", 31200, {"aws_cur.csv": ["38 vol-* + 214 snap-* whose resource_tags_user_source_instance has no BoxUsage in the last 60 days"]},
      "EBS volumes/snapshots of terminated instances. amount = Oct-2026 cost × 12 × 3.70. (DEMO status: fixed — rows kept so the evidence exists.)")

# AWS monthly invoices (sum of CUR) -> invoices + lines; paid from USD account
aws = VBY["aws"]
by_month = {}
for row in CUR:
    k = (row["bill_billing_period_start_date"][:7], row["line_item_product_code"])
    by_month[k] = by_month.get(k, 0) + row["line_item_unblended_cost"]
for i in range(24):
    lines = [(f"{p} — {ym(i)}", 1, r2(c)) for (m_, p), c in sorted(by_month.items()) if m_ == ym(i)]
    add_invoice(aws, me(i), sum(l[2] for l in lines), lines=lines, po="")

# ════════════════════════════ 6. AI usage (OpenAI + Anthropic, daily) ════════════════════════════
PRICE = {"gpt-5": (1.25, .125, 10), "gpt-5-mini": (.25, .025, 2), "gpt-4.1": (2, .5, 8), "gpt-4o-mini": (.15, .075, .6),
         "text-embedding-3-large": (.13, .13, 0), "text-embedding-3-small": (.02, .02, 0),
         "claude-opus-4-5": (5, .5, 25), "claude-sonnet-4-5": (3, .3, 15), "claude-haiku-4-5": (1, .1, 5)}
MONTHLY_AI = [52000,55000,61000,66000,72000,79000,88000,94000,101000,112000,118000,126000,131000,138000,142000,147000,151000,156000,162000,168000,171000,176000,181000,188000]
# combos: provider, project, key, owner, model, start, weight(filler)|None, avg_in, cached_frac, avg_out
COMBOS = [
 ("openai", "support-copilot", "support-copilot-prod", "EMP-1008", "gpt-5", "2024-11-01", None, 4100, 0, 450),
 ("openai", "support-copilot", "support-copilot-staging", "EMP-1008", "gpt-5-mini", "2024-11-01", .02, 3800, .3, 400),
 ("openai", "search-rerank", "search-rerank-prod", "EMP-1003", "text-embedding-3-large", "2024-11-01", .05, 350, 0, 0),
 ("openai", "search-rerank", "search-rerank-prod", "EMP-1003", "gpt-5-mini", "2024-11-01", .07, 2500, .61, 120),
 ("openai", "dan-experiments", "dan-experiments", EMP_DAN, "gpt-4.1", "2025-09-01", None, 6000, 0, 900),
 ("openai", "sales-email-drafts", "sales-drafts-prod", "EMP-1006", "gpt-5", "2025-03-01", .05, 1800, .08, 700),
 ("openai", "kb-ingest", "kb-ingest-batch", "EMP-1003", "text-embedding-3-small", "2024-11-01", .01, 900, 0, 0),
 ("openai", "eval-harness", "eval-harness-ci", "EMP-1000", "gpt-5", "2024-11-01", .05, 3000, .44, 600),
 ("openai", "agent-platform", "agent-prod-openai", "EMP-1008", "gpt-5", "2025-06-01", .14, 5200, .5, 800),
 ("openai", "agent-platform", "agent-prod-openai", "EMP-1008", "gpt-5-mini", "2025-06-01", .06, 3000, .5, 500),
 ("openai", "internal-chatbot", "slack-bot", "EMP-1004", "gpt-5-mini", "2024-11-01", .02, 2200, .2, 400),
 ("openai", "data-labeling", "labeling-batch", "EMP-1003", "gpt-4o-mini", "2024-11-01", .02, 1500, 0, 60),
 ("anthropic", "ticket-classifier", "ticket-classifier-prod", "EMP-1003", "claude-opus-4-5", "2024-11-01", None, 600, 0, 380),
 ("anthropic", "ticket-classifier", "ticket-classifier-summarize", "EMP-1003", "claude-sonnet-4-5", "2024-11-01", .10, 2400, .12, 300),
 ("anthropic", "eval-harness", "eval-harness-anthropic", "EMP-1000", "claude-sonnet-4-5", "2024-11-01", .04, 3000, .44, 600),
 ("anthropic", "code-review-bot", "code-review-ci", "EMP-1000", "claude-sonnet-4-5", "2025-02-01", .06, 9000, .35, 900),
 ("anthropic", "agent-platform", "agent-prod-anthropic", "EMP-1008", "claude-opus-4-5", "2025-06-01", .14, 6000, .55, 900),
 ("anthropic", "agent-platform", "agent-prod-anthropic", "EMP-1008", "claude-haiku-4-5", "2025-06-01", .04, 2500, .5, 300),
 ("anthropic", "data-labeling", "labeling-anthropic", "EMP-1003", "claude-haiku-4-5", "2024-11-01", .03, 1400, 0, 80),
 ("anthropic", "support-copilot", "support-copilot-fallback", "EMP-1008", "claude-sonnet-4-5", "2024-11-01", .03, 4000, .2, 450),
 ("anthropic", "research-sandbox", "research-sandbox", "EMP-1003", "claude-opus-4-5", "2025-01-01", .02, 8000, .3, 1200),
]
devs = [e for e in EMP if e["department"] == "R&D" and e["n"] > 1011 and D(e["start_date"]) < D("2026-06-01")]
dev_key_owners = [e for e in devs if not e["end_date"]][:48] + [e for e in devs if e["end_date"] and e["end_date"] not in SEAT_DEP_ENDS and e["employee_id"] not in (EMP_DAN, EMP_POST)][:2]
for k, e in enumerate(dev_key_owners):
    nm = next(l for h, l in NAMES if h == e["first_name"])
    prov = "anthropic" if k % 2 else "openai"
    COMBOS.append((prov, "dev-sandbox", f"dev-{nm}-{e['n']}", e["employee_id"], "claude-sonnet-4-5" if prov == "anthropic" else "gpt-5",
                   max(e["start_date"], "2024-11-01"), .002, 3000, .2, 500))
SEATS_USD_M = (2200 + 729) + sum(VBY[k]["annual"] for k in ("chatgpt", "claudeteam", "pinecone", "hf", "otter", "perplexity", "midjourney", "elevenlabs")) / FX / 12

def wfac(d): return .55 if d.weekday() in (4, 5) else 1.0
AI = []
def combo_active(c, d):
    if d < D(c[5]): return False
    o = emps[c[3]]
    if c[2].startswith("dev-") and o["end_date"] and d > D(o["end_date"]): return False   # personal keys revoked at offboarding (noise)
    return True
supp_req_12 = 58000 / (0.92 * 3200 * (1.25 - .125) / 1e6 * FX)   # F-1007
supp_g = [1.6 ** (i / 12) for i in range(24)]
supp_req = [supp_req_12 * supp_g[i] / sum(supp_g[12:]) for i in range(24)]
def cpr(model, ain, cf, aout):
    p = PRICE[model]; return (ain * (1 - cf) * p[0] + ain * cf * p[1] + aout * p[2]) / 1e6
for i in range(24):
    api = MONTHLY_AI[i] / FX - SEATS_USD_M
    planted = {}
    planted["support-copilot-prod"] = supp_req[i] * cpr("gpt-5", 4100, 0, 450)
    planted["ticket-classifier-prod"] = (6025.7 if i == 23 else 6025.7 * (.35 + .65 * i / 23))         # F-1001
    planted["dan-experiments"] = 0 if ms(i) < D("2025-09-01") else (1837.84 if ms(i) >= D("2026-03-01") else 1837.84 * (mi(ms(i)) - 9) / 7)   # F-1005
    fill = api - sum(planted.values())
    act = [c for c in COMBOS if c[6] and combo_active(c, ms(i))]
    sw = sum(c[6] for c in act)
    for c in COMBOS:
        prov, proj, key, owner, model, st, w, ain, cf, aout = c
        month_cost = planted[key] if w is None else (fill * w / sw if c in act else 0)
        dd = [d for d in days(ms(i), me(i)) if combo_active(c, d)]
        if not dd or month_cost <= 0: continue
        cron = key == "dan-experiments"
        wf = [1.0 if cron else wfac(d) for d in dd]
        for d, f in zip(dd, wf):
            dc = month_cost * f / sum(wf)
            if key == "support-copilot-prod":
                req = round(supp_req[i] * f / sum(wf))
            else:
                req = max(1, round(dc / cpr(model, ain, cf, aout) * (1 if cron else R.uniform(.97, 1.03))))
            jin = 1 if cron else R.uniform(.96, 1.04)
            tin = round(req * ain * jin); tc = round(tin * cf); tout = round(req * aout * (1 if cron else R.uniform(.96, 1.04)))
            p = PRICE[model]
            cost = ((tin - tc) * p[0] + tc * p[1] + tout * p[2]) / 1e6
            AI.append(dict(date=str(d), provider=prov, project=proj, api_key_name=key, api_key_owner_employee_id=owner, model=model,
                           requests=req, input_tokens=tin, cached_input_tokens=tc, output_tokens=tout, cost_usd=round(cost, 4)))
for prov in ("openai", "anthropic"):
    v = VBY[prov]
    for i in range(24):
        rows = [a for a in AI if a["provider"] == prov and a["date"][:7] == ym(i)]
        bym = {}
        for a in rows: bym[a["model"]] = bym.get(a["model"], 0) + a["cost_usd"]
        lines = [(f"{m} — API usage {ym(i)}", 1, r2(c)) for m, c in sorted(bym.items())]
        add_invoice(v, me(i), sum(l[2] for l in lines), lines=lines, po="")
plant("F-1001", "AI_MODEL_OVERKILL", "recurring", 214000, {"ai_usage.csv": ["api_key_name=ticket-classifier-prod, model=claude-opus-4-5"]},
      "classification route on the flagship model, avg 380 output tokens. amount = Oct-2026 cost × 0.80 (haiku-4-5 is 1/5 the price) × 12 × 3.70.")
plant("F-1005", "AI_KEY_ORPHAN", "recurring", 81600, {"ai_usage.csv": ["api_key_name=dan-experiments"], "employees.csv": [EMP_DAN]},
      "key owner EMP-1061 end_date 2026-07-14; daily cron continues at the same volume. amount = Oct-2026 cost × 12 × 3.70.")
plant("F-1007", "AI_NO_PROMPT_CACHE", "recurring", 58000, {"ai_usage.csv": ["api_key_name=support-copilot-prod"]},
      "cached_input_tokens = 0 on every row. amount = last-12m requests × 0.92 (share with the shared 3,200-token prefix) × 3,200 × (1.25−0.125)$/1M × 3.70.")

# ════════════════════════════ 7. SaaS seats (monthly snapshot) ════════════════════════════
TOOLS = {  # tool: (vendor_key, seat_cost_usd, {dept: prob})
 "slack": ("slack", 15, {d: 1 for d in DEPTS}), "google_workspace": ("gws", 22, {d: 1 for d in DEPTS}),
 "1password": ("1password", 7.99, {d: 1 for d in DEPTS}), "hibob": ("hibob", 10, {d: 1 for d in DEPTS}),
 "zoom": ("zoom", 15.99, {"R&D": .25, "Product": 1, "Sales": 1, "Marketing": 1, "Customer Success": 1, "G&A": 1}),
 "github": ("github", 21, {"R&D": 1, "Product": .5}), "jira": ("atlassian", 8.6, {"R&D": 1, "Product": 1}),
 "confluence": ("atlassian", 6.05, {"R&D": 1, "Product": 1, "Customer Success": 1}),
 "notion": ("notion", 10, {"G&A": 1, "Marketing": 1, "Product": .8, "R&D": .08}),
 "monday": ("monday", 30.84, {"Sales": 1, "Marketing": 1, "Customer Success": 1}),
 "cursor": ("cursor", 40, {"R&D": .92}), "copilot": ("copilot", 16.2, {}),
 "salesforce": ("salesforce", 165, {"Sales": 1}), "hubspot": ("hubspot", 100, {"Marketing": 1}),
 "gong": ("gong", 133, {"Sales": 1}), "intercom": ("intercom", 85, {"Customer Success": 1}),
 "datadog": ("datadog", 0, {"R&D": .4}), "miro": ("miro", 10, {"Product": 1, "Marketing": .6, "R&D": .2}),
 "loom": ("loom", 15, {"Customer Success": 1, "Sales": .6, "Product": .5, "Marketing": .5}),
 "canva": ("canva", 10, {"Marketing": 1, "Sales": .2}), "postman": ("postman", 19, {"R&D": .35}),
 "figma": ("figma", 0, {"R&D": .3}),   # viewers; the 22 editors are assigned below
}
def h01(*a): return int(hashlib.md5("|".join(map(str, a)).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
snap_end = me(23)
act_end = [e for e in EMP if not e["end_date"]]
figma_editors = [e for e in act_end if e["department"] in ("Product", "Marketing")] + [e for e in act_end if e["department"] == "R&D"][5:11]
figma_idle = figma_editors[3:16]                                 # 13 idle editors (F-1011)
rnd_end = sorted([e for e in act_end if e["department"] == "R&D" and e["n"] not in HEADS], key=lambda e: e["start_date"])
copilot_seats = rnd_end[:45]
copilot_idle = copilot_seats[:31]                                # F-1018: Cursor-active, Copilot unused
sf_extra = [e for e in act_end if e["department"] == "Customer Success"][:4]
hs_extra = [e for e in act_end if e["department"] == "Sales"][:7]
monday_extra = [e for e in act_end if e["department"] == "Product"][:8]
jira_extra = [e for e in act_end if e["department"] == "Customer Success"][:4]
SEATS = []
SEAT6 = ("slack", "google_workspace", "github", "notion", "zoom", "1password")
for i in range(24):
    snap = me(i)
    for tool, (vk, cost, probs) in TOOLS.items():
        for e in EMP:
            dep_keep = e in seat_departed and tool in SEAT6 and D(e["start_date"]) <= snap
            if not active_on(e, snap) and not dep_keep: continue
            has = h01(tool, e["employee_id"]) < probs.get(e["department"], 0)
            seat_type, c = "member", cost
            if tool == "figma":
                if e in figma_editors: has, seat_type, c = True, "editor", 70.6
                else: seat_type = "viewer"
            if tool == "copilot": has = e in copilot_seats and ms(i) >= D("2025-01-01")
            if tool == "cursor" and e in copilot_idle: has = True
            if tool == "salesforce" and e in sf_extra: has = True
            if tool == "hubspot" and e in hs_extra: has = True
            if tool == "monday" and e in monday_extra: has = True
            if tool == "jira" and e in jira_extra: has = True
            if e in seat_departed and tool in SEAT6: has = True
            if not has: continue
            if tool in ("salesforce", "github", "jira", "hubspot") and e["n"] in HEADS: seat_type = "admin"
            # activity
            if not active_on(e, snap):
                la, acts = D(e["end_date"]), 0
            elif tool == "figma" and e in figma_idle and snap >= D("2026-02-28"):
                la, acts = min(snap, D("2026-02-01")) - timedelta(int(h01("fi", e["n"]) * 120)), 0
            elif tool == "copilot" and e in copilot_idle and snap >= D("2025-09-30"):
                la, acts = D("2025-09-01") - timedelta(int(h01("ci", e["n"]) * 60)), 0
            else:
                la = snap - timedelta(R.randint(0, 9)); acts = R.randint(4, 420)
            la = max(la, D(e["start_date"]))
            SEATS.append(dict(snapshot_date=str(snap), tool=tool, vendor_id=VBY[vk]["vendor_id"], employee_id=e["employee_id"],
                              seat_type=seat_type, seat_cost_usd_month=c if seat_type != "viewer" else 0,
                              last_active_date=str(la), actions_30d=acts))
plant("F-1011", "LICENSE_UNUSED", "recurring", 41000, {"saas_seats.csv": [f"figma|{e['employee_id']}|2026-10-31" for e in figma_idle]},
      "Oct-2026 snapshot: 22 Figma editor seats, 13 with last_active_date > 90 days and 0 actions. amount = 13 × seat_cost_usd_month × 12 × 3.70.")
plant("F-1015", "LICENSE_DEPARTED", "recurring", 28400, {"saas_seats.csv": [f"{e['employee_id']}" for e in seat_departed], "employees.csv": [e["employee_id"] for e in seat_departed]},
      "Oct-2026 snapshot rows of 7 terminated employees in Slack, Google Workspace, GitHub, Notion, Zoom, 1Password. amount = Σ seat_cost_usd_month × 12 × 3.70.")
plant("F-1018", "AI_SEAT_OVERLAP", "recurring", 22300, {"saas_seats.csv": [f"copilot|{e['employee_id']}" for e in copilot_idle]},
      "Oct-2026: 31 users with Cursor actions_30d>0 and Copilot actions_30d=0. amount = Σ copilot seat_cost × 12 × 3.70.")
plant("F-1008", "LICENSE_DUPLICATE_FUNC", "recurring", 52000, {"saas_seats.csv": ["tool in (jira, monday) snapshot 2026-10-31"], "card_transactions.csv": ["merchant=MONDAY.COM"]},
      "Jira (R&D+Product) and monday.com (Sales/Marketing/CS + 8 Product) both in use, 12 users in both. amount = last-12m monday.com card spend (charged_ils).")

# ════════════════════════════ 8. Special vendors (card/AP plants) ════════════════════════════
for i in range(24):
    d = date(*MONTHS[i], 4)
    add_card(VBY["figma"], d, 22 * 70.6)                              # identical monthly charges (noise trap)
    add_card(VBY["monday"], date(*MONTHS[i], 9), 1172.0)
    add_card(VBY["cursor"], date(*MONTHS[i], 1), 2200.0)
    if ms(i) >= D("2025-01-01"): add_card(VBY["copilot"], date(*MONTHS[i], 2), 45 * 16.2)
# MongoDB: monthly card charges on the 3rd; 03/08/2026 = INV-ATL-88213 $10,450 (July usage spike)
mg = VBY["mongodb"]
base_mg = (182000 - 10450 * fx(D("2026-08-03"))) / 11 / FX
for i in range(24):
    d = date(*MONTHS[i], 3)
    if d == D("2026-08-03"):
        add_card(mg, d, 10450.0)
    else:
        add_card(mg, d, base_mg * g(i, .12) / (norm12(.12) / 12) * (1 + R.uniform(-.05, .05)) * (1 if i >= 12 else 1))
mdb = add_invoice(mg, D("2026-08-01"), 10450.0, lines=[("MongoDB Atlas — Dedicated clusters, July 2026", 1, 10450.0)],
                  number="INV-ATL-88213", paid=D("2026-08-11"), po="")
BANK[-1].update(account="ILS", debit=38900.0, description="העברה מקוונת - MongoDB Inc INV-ATL-88213")
mdb["notes"] = "שולם בהעברה בש״ח"
plant("F-1012", "DUP_CROSS_CURRENCY", "recovery", 38900,
      {"invoices.csv": [mdb["ap_doc_id"]], "card_transactions.csv": ["MONGODB CLOUD 2026-08-03 USD 10,450"], "bank_transactions.csv": ["ILS 2026-08-11 debit 38,900 'MongoDB Inc INV-ATL-88213'"]},
      "same Atlas invoice charged $10,450 on the Cal card (03/08/2026) and paid again ₪38,900 by bank transfer (11/08/2026). amount = the bank debit.")
# Notion: annual card renewal 12/05 + (2026) also paid via AP invoice 20/05
nt = VBY["notion"]
add_card(nt, D("2025-05-12"), 28 * 10 * 12)
nc = add_card(nt, D("2026-05-12"), 32 * 10 * 12)
ninv = add_invoice(nt, D("2026-05-12"), 3840.0, lines=[("Notion Plus — 32 seats, annual (05/2026–05/2027)", 32, 120.0)],
                   number="NOTION-2026-0512-8841", paid=D("2026-05-20"), po="")
plant("F-1022", "DUP_CARD_AND_AP", "recovery", 14200,
      {"card_transactions.csv": [f"NOTION LABS, INC. 2026-05-12 voucher {nc['voucher']}"], "invoices.csv": [ninv["ap_doc_id"]]},
      "annual Notion renewal charged on card 12/05/2026 and the same invoice paid by bank transfer 20/05/2026. amount = card charged_ils.")
# HubSpot: annual renewal 01/10, 140,000 -> 187,500 ₪, same 14 seats
hs = VBY["hubspot"]
hub = []
for d, a in ((D("2025-10-01"), 140000.0), (D("2026-10-01"), 187500.0)):
    hub.append(add_invoice(hs, d, a, lines=[(f"Sales Hub Professional — 14 seats, annual {d.year}-{d.year + 1}", 14, r2(a / 14))], po=""))
for d in (D("2024-11-01"), D("2025-01-01")): pass
plant("F-1009", "AUTO_RENEWAL_JUMP", "recurring", 47500, {"invoices.csv": [h_["ap_doc_id"] for h_ in hub], "vendors.csv": [hs["vendor_id"]]},
      "auto_renew=TRUE; renewal 01/10/2026 ₪187,500 vs ₪140,000 a year earlier, 14 seats both years. amount = difference.")
# Datadog: monthly invoice, one line is indexed DEBUG logs (F-1004)
dd_ = VBY["datadog"]
DBG = 88000 / FX / 12
for i in range(24):
    tot = 410000 / FX * g(i, .22) / norm12(.22) * (1 + R.uniform(-.03, .03))
    dbg = DBG if i >= 12 else DBG * (.6 + .4 * i / 12)
    other_idx = dbg * 39 / 61
    rest = tot - dbg - other_idx
    lines = [("Infrastructure Hosts (Pro)", 1, r2(rest * .45)), ("APM Hosts", 1, r2(rest * .3)), ("Log Ingestion (GB)", 1, r2(rest * .2)),
             ("Indexed Logs 15d — status:debug", 1, r2(dbg)), ("Indexed Logs 15d — status:info,warn,error", 1, r2(other_idx)),
             ("Synthetics API tests", 1, r2(rest * .05))]
    add_invoice(dd_, me(i), sum(l[2] for l in lines), lines=lines, po="")
plant("F-1004", "SAAS_TIER_OVERKILL", "recurring", 88000, {"invoices.csv": ["Datadog lines 'Indexed Logs 15d — status:debug'"], "invoice_lines.csv": ["description contains status:debug"]},
      "61% of indexed log spend is DEBUG level. amount = last-12m 'status:debug' invoice lines USD × 3.70.")
# קוד-פלוס: 4 × ₪18,500 within 25 days (approval threshold ₪20,000) + one older legit invoice
cp = VBY["codeplus"]
add_invoice(cp, D("2025-07-08"), 12000.0, lines=[("אפיון תהליכי מכירה", 1, 12000.0)], po="PO-2511")
split = [add_invoice(cp, d, 18500.0, lines=[(f"פרויקט אינטגרציית Salesforce — שלב {k}", 1, 18500.0)], po="")
         for k, d in enumerate([D("2026-03-03"), D("2026-03-10"), D("2026-03-19"), D("2026-03-27")], 1)]
plant("F-1026", "INVOICE_SPLITTING", "review", 74000, {"invoices.csv": [s["ap_doc_id"] for s in split]},
      "4 invoices of ₪18,500 pre-VAT from one vendor within 25 days, each just under the ₪20,000 VP-approval threshold, no PO. amount = sum pre-VAT.")
# שמיר-כהן: invoice 2026-0412 entered twice in AP and paid twice, 9 days apart
law = VBY["law"]
dups = []
for paid in (D("2026-05-14"), D("2026-05-24")):
    dups.append(add_invoice(law, D("2026-04-14"), 19830.51, number="2026-0412", paid=paid, po="",
                            lines=[("ייעוץ משפטי — הסכם השקעה והסכמי לקוחות, מרץ 2026", 1, 19830.51)]))
dups[1]["allocation_number"] = dups[0]["allocation_number"]
plant("F-1017", "DUP_INVOICE_EXACT", "recovery", 23400, {"invoices.csv": [x["ap_doc_id"] for x in dups], "bank_transactions.csv": ["2 ILS debits 23,400 to שמיר-כהן"]},
      "same vendor + invoice_number 2026-0412 + same total ₪23,400, two separate AP entries and two bank transfers 9–10 days apart. amount = one total.")
# F-1020: 6 invoices above the allocation-number threshold without allocation_number (VAT 18% total 19,800)
NOALLOC = [("talent", "2025-06-17", 24000.0, "דמי השמה — Senior Backend Engineer"), ("cyber", "2025-09-08", 21000.0, "מבדק חדירות — אפליקציית ווב"),
           ("law", "2026-02-11", 15500.0, "ייעוץ משפטי — דיני עבודה, ינואר 2026"), ("tax", "2026-04-06", 12500.0, "ייעוץ מס — רבעון 1"),
           ("studio", "2026-07-13", 19000.0, "עיצוב קמפיין השקה Q3"), ("pr", "2026-08-04", 18000.0, "קמפיין יח״צ — כנס Cyber Week")]
noalloc = [add_invoice(VBY[k], D(d), a, lines=[(t, 1, a)], alloc="", number="2026-0187" if k == "law" else None) for k, d, a, t in NOALLOC]
plant("F-1020", "INVOICE_NO_ALLOCATION", "recovery", 19800, {"invoices.csv": [x["ap_doc_id"] for x in noalloc]},
      "Israeli tax invoices with amount_before_vat above the Tax Authority threshold for their issue_date and an empty allocation_number. VAT is not deductible. amount = Σ vat_amount.")
# NOISE: cancelled + reissued invoice (accountant)
cpa = VBY["cpa"]
c1 = add_invoice(cpa, D("2025-07-06"), 15254.24, number="2025-1187", status="cancelled", lines=[("הנהלת חשבונות — יוני 2025 (סכום שגוי)", 1, 15254.24)], po="")
c2 = add_invoice(cpa, D("2025-07-09"), 13983.05, number="2025-1188", lines=[("הנהלת חשבונות — יוני 2025 (מתוקן)", 1, 13983.05)], po="")
c1["notes"] = "בוטלה — הוחלפה ב-2025-1188"; c2["notes"] = "מחליפה את 2025-1187"
NOISE.append(dict(trap="cancelled_and_reissued_invoice", rows={"invoices.csv": [c1["ap_doc_id"], c2["ap_doc_id"]]},
                  why="2025-1187 status=cancelled, reissued as 2025-1188 with a corrected amount; only one payment. Not a duplicate."))

# generic vendors
for v in VENDORS:
    if v["sched"] != "special": generic(v)

# NOISE: Zoom refund
zr = VBY["zoom"]
z1 = add_card(zr, D("2026-03-05"), 159.90)
z2 = add_card(zr, D("2026-03-09"), -159.90, kind="זיכוי")
z2["fx_fee_ils"] = -z1["fx_fee_ils"]; z2["charged_ils"] = -z1["charged_ils"]
NOISE.append(dict(trap="card_refund", rows={"card_transactions.csv": [z1["voucher"], z2["voucher"]]},
                  why="Zoom Webinar add-on charged by mistake and refunded 4 days later (transaction_type=זיכוי). Net zero, not a duplicate."))
NOISE.append(dict(trap="recurring_identical_saas_charges", rows={"card_transactions.csv": ["FIGMA, MONDAY.COM, CURSOR, 1PASSWORD, ZOOM … same amount every month"]},
                  why="fixed-seat subscriptions bill the same amount every month on the same day — different months, not duplicates."))

# ════════════════════════════ 9. Telecom / utilities / cars ════════════════════════════
TEL = []
roam_lines = [e for e in EMP if e["department"] == "Sales" and not e["end_date"] and e["n"] > 1011][3:7]
pkg_lines = {e["employee_id"] for e in EMP if e["department"] == "Sales" and not e["end_date"]} - {e["employee_id"] for e in roam_lines} | {"EMP-1006", "EMP-1007"}
roam_plan = {}
for e in roam_lines:   # F-1025: per-use roaming; last-12m total exactly 6,300
    trips = set(R.sample(range(24), 5)) | {R.randint(12, 23)}
    roam_plan[e["employee_id"]] = trips
tot12 = sum(1 for t in roam_plan.values() for i in t if i >= 12)
roam_each = 6300 / tot12
for i in range(24):
    for e in EMP:
        st, en = D(e["start_date"]), edate(e, "end_date")
        keep = e in phone_departed and en and en < ms(i)
        if st > me(i): continue
        if en and en < ms(i) and not keep: continue
        pkg = e["employee_id"] in pkg_lines
        fee = 129.0 if pkg else 89.0
        if keep or (en and en < me(i) and e in phone_departed and en < ms(i)):
            mins, gb = 0, 0.0
        else:
            mins, gb = R.randint(120, 1400), round(R.uniform(1.5, 28), 1)
        roam = 0.0
        if e["employee_id"] in roam_plan and i in roam_plan[e["employee_id"]]:
            roam = r2(roam_each * R.uniform(.999, 1.001)) if i >= 12 else r2(roam_each * R.uniform(.6, 1.2))
        TEL.append(dict(billing_month=ym(i), line_id=e["phone_line_id"], employee_id=e["employee_id"],
                        plan="עסקי 129 + חבילת חו״ל" if pkg else "עסקי 89", monthly_fee=fee, minutes=mins, data_gb=gb,
                        roaming_charges=roam, extras=0.0, total=r2(fee + roam)))
# fix rounding so last-12 roaming is exactly 6,300
rl = [t for t in TEL if t["roaming_charges"] and t["billing_month"] >= "2025-11"]
rl[-1]["roaming_charges"] = r2(6300 - sum(t["roaming_charges"] for t in rl[:-1])); rl[-1]["total"] = r2(rl[-1]["monthly_fee"] + rl[-1]["roaming_charges"])
for i in range(24):
    rows = [t for t in TEL if t["billing_month"] == ym(i)]
    pl = [(f"{t['line_id']} — {t['plan']}", 1, t["monthly_fee"]) for t in rows] +          [(f"{t['line_id']} — נדידה לפי שימוש", 1, t["roaming_charges"]) for t in rows if t["roaming_charges"]]
    add_invoice(VBY["partner"], date(*MONTHS[i], 20), sum(t["total"] for t in rows), lines=pl, po="")
plant("F-1024", "PHONE_LINE_DEPARTED", "recurring", 9600, {"telecom.csv": [e["phone_line_id"] for e in phone_departed], "employees.csv": [e["employee_id"] for e in phone_departed]},
      "9 lines whose owner is terminated in HiBob, 0 minutes / 0 GB for 60+ days, still billed ₪89. amount = 9 × 89 × 12.")
plant("F-1025", "PHONE_ROAMING", "recurring", 6300, {"telecom.csv": [e["phone_line_id"] for e in roam_lines]},
      "4 lines on plan 'עסקי 89' (no abroad package) with per-use roaming_charges. amount = last-12m roaming_charges. (DEMO status: reviewed_ok)")
NOISE.append(dict(trap="departed_lines_disconnected", rows={"telecom.csv": ["lines of the other 14 departed employees end at their end_date"]},
                  why="properly offboarded lines stop billing — must not be flagged."))
# Utilities — IEC monthly bill
KWH25 = {11: 7200, 12: 7600, 1: 7900, 2: 7500, 3: 7100, 4: 7000, 5: 7600, 6: 8600, 7: 9400, 8: 10100, 9: 8400, 10: 8400}
UTIL = []
for i in range(24):
    y, m = MONTHS[i]
    k = KWH25[m] * (0.97 if ms(i) < D("2025-01-01") else 1.0 if ms(i) < D("2025-11-01") else 1.04)
    if ym(i) in ("2026-09", "2026-10"): k = 11900                          # F-1021
    rate = .4150 if y == 2024 else .4210 if y == 2025 else .4286
    k = round(k)
    kc, fc = r2(k * rate), 4980.0
    sub = r2(kc + fc); va = r2(sub * vat_rate(ms(i)))
    UTIL.append(dict(billing_period=ym(i), period_start=str(ms(i)), period_end=str(me(i)), meter_id="IEC-MTR-4471902", contract_account="346612078",
                     tariff="כללי", kwh=k, kwh_rate=rate, kwh_charge=kc, fixed_charge=fc, subtotal=sub, vat=va, total=r2(sub + va)))
    add_invoice(VBY["iec"], me(i), sub,
                lines=[("צריכת חשמל — תעריף כללי", k, rate), ("תשלום קבוע וקיבולת", 1, fc)], po="")
plant("F-1021", "UTILITY_SPIKE", "recurring", 18000, {"utilities.csv": ["2026-09", "2026-10", "2025-09", "2025-10"]},
      "Sep–Oct 2026 11,900 kWh/month vs 8,400 a year earlier (+41%). amount = excess kWh × 2026 kwh_rate × 6 (annualize 2 months).")
NOISE.append(dict(trap="seasonal_august_electricity", rows={"utilities.csv": ["2025-08", "2026-08"]},
                  why="August is the yearly peak (AC); Aug-2026 is +4% YoY like the rest of the year — seasonal, not a spike."))
# Car leases (Albar) + fuel (Paz)
CARS = []
MODELS = ["Skoda Octavia", "Hyundai Ioniq 5", "Toyota Corolla Hybrid", "Kia Niro EV", "Tesla Model 3", "Mazda CX-5", "Skoda Superb", "Hyundai Tucson", "Volvo XC40"]
for k, eid in enumerate(CAR_EMPS):
    e = emps[eid]
    model = "BMW i4" if eid == EMP_CAR else MODELS[k % len(MODELS)]
    fee = 5900.0 if eid == EMP_CAR else round(3850 * R.uniform(.85, 1.15), 0)
    plate = f"{R.randint(10, 99)}-XXX-{R.randint(10, 99)}"
    ret = e["end_date"]
    for i in range(24):
        if D(e["start_date"]) > me(i): continue
        returned = ret and D(ret) < ms(i)
        if returned and not (eid == EMP_CAR and ym(i) in ("2026-08", "2026-09")): continue
        ev = "EV" in model or "Ioniq" in model or "Tesla" in model or "i4" in model
        CARS.append(dict(billing_month=ym(i), plate_masked=plate, employee_id=eid, model=model, monthly_fee=fee,
                         fuel_card_ils=0.0 if (returned or ev) else r2(R.uniform(700, 1700)), km=0 if returned else R.randint(900, 3200),
                         returned_date=ret or ""))
for i in range(24):
    rows = [c for c in CARS if c["billing_month"] == ym(i)]
    for c in rows:   # Albar and Paz issue one invoice per vehicle / fuel card
        lease, ins = r2(c["monthly_fee"] * .82), r2(c["monthly_fee"] - r2(c["monthly_fee"] * .82))
        add_invoice(VBY["albar"], date(*MONTHS[i], 1), c["monthly_fee"], po="",
                    lines=[(f"דמי ליסינג תפעולי {c['plate_masked']} {c['model']}", 1, lease), (f"ביטוח ותחזוקה {c['plate_masked']}", 1, ins)])
        if c["fuel_card_ils"]:
            k = R.randint(3, 6); parts = [r2(c["fuel_card_ils"] / k)] * (k - 1)
            parts.append(r2(c["fuel_card_ils"] - sum(parts)))
            add_invoice(VBY["paz"], me(i), c["fuel_card_ils"], po="",
                        lines=[(f"תדלוק {c['plate_masked']} — תחנת פז #{R.randint(100, 480)}", 1, x) for x in parts])
plant("F-1023", "CAR_LEASE_DEPARTED", "recovery", 11800, {"car_leases.csv": [f"{EMP_CAR}|2026-08", f"{EMP_CAR}|2026-09"], "employees.csv": [EMP_CAR]},
      "car returned 2026-07-31 (returned_date) yet lease charged for 08 and 09/2026, km=0. amount = Σ monthly_fee after returned_date.")
NOISE.append(dict(trap="car_returned_properly", rows={"car_leases.csv": [car_noise["employee_id"]]},
                  why=f"{car_noise['employee_id']} left {CAR_NOISE_END}; car returned and charges stopped the same month."))
NOISE.append(dict(trap="departed_seats_released", rows={"saas_seats.csv": [released_noise["employee_id"]]},
                  why=f"{released_noise['employee_id']} left {released_noise['end_date']}; every seat disappears from the next snapshot (and 15 more departed employees behave the same)."))
NOISE.append(dict(trap="prorated_final_payslip", rows={"payroll.csv": [f"{prorate_noise['employee_id']}|2026-10"]},
                  why=f"{prorate_noise['employee_id']} left {PRORATE_NOISE_END}; the October payslip is prorated to 15 days — legitimate final pay."))
NOISE.append(dict(trap="revoked_personal_api_keys", rows={"ai_usage.csv": [c[2] for c in COMBOS if c[2].startswith("dev-") and emps[c[3]]["end_date"]]},
                  why="personal dev keys of departed engineers stop on their end_date — revoked correctly."))
plant("F-1016", "FX_CARD_FEES", "recurring", 27000, {"card_transactions.csv": ["original_currency=USD (fx_fee_ils)"]},
      "≈₪1.08M/yr of USD subscriptions on the Cal card, each with a 2.5% foreign-transaction fee, while a USD account exists. amount = last-12m Σ fx_fee_ils.")

# ════════════════════════════ 10. Bank (Leumi-like) ════════════════════════════
pr = {}
for p in PAYROLL: pr.setdefault(p["period"], []).append(p)
for i in range(24):
    rows = pr[ym(i)]
    pd_ = pay_day(i)
    BANK.append(dict(account="ILS", date=pd_, value_date=pd_, description=f"מס״ב משכורות {MONTHS[i][1]:02d}/{MONTHS[i][0]}",
                     reference=f"MSV{MONTHS[i][0]}{MONTHS[i][1]:02d}", debit=r2(sum(p["net"] for p in rows)), credit=0.0))
    d15 = biz(date(*MONTHS[i], 15) + timedelta(days=dim(i)))
    if d15 <= END:
        for desc, amt in (("מס הכנסה - ניכויים במקור", sum(p["income_tax"] for p in rows)),
                          ("ביטוח לאומי - דיווח 102", sum(p["bituach_leumi_employer"] + p["bituach_leumi_employee"] for p in rows)),
                          ("הפקדה לקופות גמל ופנסיה", sum(p["pension_employer"] + p["severance_employer"] + p["keren_hishtalmut_employer"] + p["pension_employee"] + p["keren_hishtalmut_employee"] for p in rows))):
            BANK.append(dict(account="ILS", date=d15, value_date=d15, description=desc, reference=f"GOV{R.randint(100000, 999999)}", debit=r2(amt), credit=0.0))
# card settlements on the 10th
bills = {}
for c in CARD: bills[c["billing_date"]] = bills.get(c["billing_date"], 0) + c["charged_ils"] + c["fx_fee_ils"]
for bd, amt in sorted(bills.items()):
    if D(bd) <= END:
        d = biz(D(bd))
        BANK.append(dict(account="ILS", date=d, value_date=d, description="כאל - חיוב כרטיסי אשראי עסקיים", reference=f"CAL{bd.replace('-', '')}", debit=r2(amt), credit=0.0))
# customer receipts (USD)
CUSTOMERS = ["Northwind Retail Inc", "Blue Harbor Insurance", "Kestrel Logistics", "Maple & Finch Bank", "Orion Telecom GmbH", "Sunline Airways",
             "Cobalt Health Ltd", "Riverstone Utilities", "Atlas Mobility BV", "Granite Credit Union", "Pioneer Foods Co", "Lumen Media Group",
             "Vantage Rail plc", "Harbor Pet Supplies", "Quantum Grid AG", "Silverleaf Hotels", "Brightpath Education", "Evergreen Mutual",
             "Nordic Parcel AB", "Crescent Energy", "Tidewater Bank", "Summit Outdoor", "Polar Telecom", "Redwood Clinics", "Meridian Travel"]
for i in range(24):
    rev = 520000 * 1.55 ** (i / 12)
    payers = R.sample(CUSTOMERS, 18)
    ws = [R.uniform(.3, 2) for _ in payers]
    for c, w in zip(payers, ws):
        d = biz(date(*MONTHS[i], R.randint(1, 27)))
        BANK.append(dict(account="USD", date=d, value_date=d, description=f"SWIFT IN - {c}", reference=f"INV-TS-{R.randint(10000, 99999)}", debit=0.0, credit=r2(rev * w / sum(ws))))
NOISE.append(dict(trap="vendor_refund_credit", rows={"bank_transactions.csv": ["ILS credit 'זיכוי מספק - גובה הפקדות אירועים'"]},
                  why="event-production vendor refunded a cancelled date — a credit, not a payment."))
BANK.append(dict(account="ILS", date=D("2026-02-17"), value_date=D("2026-02-17"), description="זיכוי מספק - גובה הפקות אירועים", reference="RFD55102", debit=0.0, credit=8260.0))
# FX conversions + fees
for i in range(24):
    out_ils = sum(b["debit"] - b["credit"] for b in BANK if b["account"] == "ILS" and ms(i) <= b["date"] <= me(i) and not b["description"].startswith("המרת"))
    conv_ils = math.ceil(out_ils / 100000) * 100000
    d = biz(date(*MONTHS[i], 2))
    rate = fx(d)
    ref = f"FX{MONTHS[i][0]}{MONTHS[i][1]:02d}"
    BANK.append(dict(account="ILS", date=d, value_date=d, description="המרת מט״ח - מחשבון דולרי", reference=ref, debit=0.0, credit=float(conv_ils)))
    BANK.append(dict(account="USD", date=d, value_date=d, description=f"המרת מט״ח לחשבון שקלי @{rate}", reference=ref, debit=r2(conv_ils / rate), credit=0.0))
    nt = sum(1 for b in BANK if b["account"] == "ILS" and ms(i) <= b["date"] <= me(i) and b["description"].startswith(("העברה", "הוראת")))
    nu = sum(1 for b in BANK if b["account"] == "USD" and ms(i) <= b["date"] <= me(i) and b["description"].startswith("SWIFT OUT"))
    lb = biz_back(me(i))
    BANK.append(dict(account="ILS", date=lb, value_date=lb, description="עמלות ניהול חשבון והעברות", reference=f"FEE{ym(i)}", debit=r2(450 + 6.5 * nt), credit=0.0))
    BANK.append(dict(account="ILS", date=d, value_date=d, description="עמלת המרת מט״ח", reference=ref, debit=r2(conv_ils * .0015), credit=0.0))
    BANK.append(dict(account="USD", date=lb, value_date=lb, description="SWIFT fees", reference=f"FEE{ym(i)}", debit=r2(25 * nu), credit=0.0))
BANK.sort(key=lambda b: (b["account"], b["date"], b["credit"] == 0))
bal = {"ILS": 21_500_000.0, "USD": 31_000_000.0}
for b in BANK:
    bal[b["account"]] = r2(bal[b["account"]] - b["debit"] + b["credit"])
    b["balance"] = bal[b["account"]]; b["currency"] = b["account"]
    b["account"] = "10-912-0004417/52 (ILS)" if b["account"] == "ILS" else "10-912-0004417/97 (USD)"
    b["date"] = str(b["date"]); b["value_date"] = str(b["value_date"])

# ════════════════════════════ 11. WRITE ════════════════════════════
counts = {}
counts["employees.csv"] = write("employees.csv", EMP, ["employee_id", "first_name", "department", "title", "start_date", "end_date", "employment_status", "manager_id", "location", "bank_account_hash", "car_lease", "phone_line_id"])
counts["payroll.csv"] = write("payroll.csv", PAYROLL, list(PAYROLL[0].keys()))
counts["vendors.csv"] = write("vendors.csv", VENDORS, ["vendor_id", "name", "category", "country", "billing_currency", "payment_method", "owner", "hp_number", "card_descriptor", "contract_end", "auto_renew"])
INVOICES.sort(key=lambda r: (r["issue_date"], r["ap_doc_id"]))
counts["invoices.csv"] = write("invoices.csv", INVOICES, list(INVOICES[0].keys()))
counts["invoice_lines.csv"] = write("invoice_lines.csv", LINES, list(LINES[0].keys()))
counts["bank_transactions.csv"] = write("bank_transactions.csv", BANK, ["account", "currency", "date", "value_date", "description", "reference", "debit", "credit", "balance"])
CARD.sort(key=lambda r: (r["transaction_date"], r["card_last4"]))
counts["card_transactions.csv"] = write("card_transactions.csv", CARD, list(CARD[0].keys()))
counts["aws_cur.csv"] = write("aws_cur.csv", CUR, list(CUR[0].keys()))
AI.sort(key=lambda r: (r["date"], r["provider"], r["api_key_name"]))
counts["ai_usage.csv"] = write("ai_usage.csv", AI, list(AI[0].keys()))
counts["saas_seats.csv"] = write("saas_seats.csv", SEATS, list(SEATS[0].keys()))
counts["telecom.csv"] = write("telecom.csv", TEL, list(TEL[0].keys()))
counts["utilities.csv"] = write("utilities.csv", UTIL, list(UTIL[0].keys()))
counts["car_leases.csv"] = write("car_leases.csv", CARS, list(CARS[0].keys()))
GT.sort(key=lambda x: x["finding_id"])
assert len(GT) == 26, len(GT)
json.dump(dict(company="טכנוסיס בע״מ", synthetic=True, seed=42, period=["2024-11-01", "2026-10-31"], usd_ils_for_annualizing=FX,
               source="design/v2/assets/demo-data.js", planted=GT, noise_traps=NOISE, row_counts=counts),
          open(OUT / "ground_truth.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2, default=str)

# ════════════════════════════ 12. RECEIPTS (HTML + PNG) ════════════════════════════
CSS = """*{box-sizing:border-box}body{margin:0;background:#ecebe6;font:14px/1.45 'Segoe UI',Arial,sans-serif;color:#1d1d1b;padding:20px}
.doc{position:relative;width:860px;margin:auto;background:#fff;padding:36px 40px;box-shadow:0 1px 4px rgba(0,0,0,.15);overflow:hidden}
.wm{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;z-index:5}
.wm span{transform:rotate(-28deg);font-size:76px;font-weight:800;color:rgba(190,20,20,.14);border:7px solid rgba(190,20,20,.14);padding:6px 30px;white-space:nowrap}
.top{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:3px solid var(--c,#333);padding-bottom:14px;margin-bottom:18px}
.brand{font-size:26px;font-weight:800;color:var(--c,#333);letter-spacing:.5px}.brand small{display:block;font-size:12px;font-weight:400;color:#666;letter-spacing:0}
h1{font-size:20px;margin:0 0 4px}.meta{display:grid;grid-template-columns:1fr 1fr;gap:4px 28px;margin:12px 0 18px;font-size:13px}
.meta b{display:inline-block;min-width:150px;color:#555;font-weight:600}table{width:100%;border-collapse:collapse;font-size:13px}
th{background:#f2f2ef;text-align:start;padding:7px 8px;border-bottom:1px solid #ccc}td{padding:6px 8px;border-bottom:1px solid #eee}
td.n,th.n{text-align:end;font-variant-numeric:tabular-nums;white-space:nowrap}.tot{margin-top:14px;margin-inline-start:auto;width:340px}
.tot td{border:none;padding:3px 8px}.tot tr:last-child td{font-weight:800;font-size:15px;border-top:2px solid #333}
.flag{background:#fff3cd;outline:2px dashed #d39e00}.foot{margin-top:22px;font-size:11px;color:#777;border-top:1px solid #ddd;padding-top:8px}"""


def money(x, cur="ILS"): return f"₪{x:,.2f}" if cur == "ILS" else f"${x:,.2f}"


def receipt(fname, title, color, brand, brand_sub, meta, head, rows, totals, rtl=True, foot=""):
    """meta: [(label, value)], rows: [tuple]; a label/first cell starting with '!' is highlighted."""
    num = lambda j, n: j > 0 and j >= n - 3 and n > 1
    m = "".join(f"<div class='{'flag' if k.startswith('!') else ''}'><b>{k.lstrip('!')}</b> {v}</div>" for k, v in meta)
    th = "".join(f"<th class='{'n' if num(j, len(head)) else ''}'>{h}</th>" for j, h in enumerate(head))
    tr = "".join("<tr" + (" class='flag'" if str(r_[0]).startswith("!") else "") + ">" + "".join(
        f"<td class='{'n' if num(j, len(r_)) else ''}'>{str(c).lstrip('!')}</td>" for j, c in enumerate(r_)) + "</tr>" for r_ in rows)
    tt = "".join(f"<tr><td>{k}</td><td class='n'>{v}</td></tr>" for k, v in totals)
    html = f"""<!doctype html><html lang="{'he' if rtl else 'en'}" dir="{'rtl' if rtl else 'ltr'}"><head><meta charset="utf-8"><title>{title}</title>
<style>{CSS}</style></head><body><div class="doc" style="--c:{color}"><div class="wm"><span>SYNTHETIC · דוגמה</span></div>
<div class="top"><div class="brand">{brand}<small>{brand_sub}</small></div><div><h1>{title}</h1></div></div>
<div class="meta">{m}</div><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table><table class="tot">{tt}</table>
<div class="foot">{foot}{' · ' if foot else ''}מסמך סינתטי לצורכי הדגמה בלבד, כל הנתונים בדויים · Synthetic sample document, not a real invoice.</div></div></body></html>"""
    (OUT / "receipts").mkdir(exist_ok=True)
    (OUT / "receipts" / fname).write_text(html, encoding="utf-8", newline="\n")
    return fname


def inv_lines(doc): return [l for l in LINES if l["ap_doc_id"] == doc]
def find_inv(vk, **kw): return next(x for x in INVOICES if x["vendor_id"] == VBY[vk]["vendor_id"] and all(x[k] == v for k, v in kw.items()))


def build_receipts():
    out = []
    TH = "טכנוסיס בע״מ · ח.פ. 515873214 · תל אביב"
    for vk, brand, color, sub in (("aws", "aws", "#232f3e", "Amazon Web Services EMEA SARL · Luxembourg"),
                                  ("openai", "OpenAI", "#10a37f", "OpenAI, LLC · San Francisco, CA"),
                                  ("anthropic", "ANTHROPIC", "#c96442", "Anthropic, PBC · San Francisco, CA")):
        x = find_inv(vk, issue_date="2026-10-31")
        out.append(receipt(f"receipt_{vk}_2026-10.html", "Invoice", color, brand, sub,
            [("Invoice number", x["invoice_number"]), ("Invoice date", x["issue_date"]), ("Bill to", "Technosis Ltd, Tel Aviv, Israel"),
             ("Billing period", "Oct 1 – Oct 31, 2026"), ("Due date", x["due_date"]), ("VAT", "Reverse charge (Israel)")],
            ["Description", "Amount (USD)"], [(l["description"], f"{l['amount']:,.2f}") for l in inv_lines(x["ap_doc_id"])],
            [("Subtotal", money(x["amount_before_vat"], "USD")), ("Tax", "$0.00"), ("Total due", money(x["total"], "USD"))], rtl=False))
    x = next(i for i in INVOICES if i["invoice_number"] == "2026-0187")
    out.append(receipt("receipt_law_2026-0187.html", f"חשבונית מס {x['invoice_number']}", "#4a3b2a", "שמיר-כהן",
        f"עורכי דין · ע.מ. {VBY['law']['hp_number']} · רמת גן (משרד בדוי)",
        [("לכבוד", TH), ("תאריך", x["issue_date"]), ("תנאי תשלום", "שוטף + 30"), ("לתשלום עד", x["due_date"]),
         ("!מספר הקצאה", "<span style='color:#b00'>לא צוין</span>"), ("הזמנת רכש", "—")],
        ["תיאור", "סכום ₪"], [(l["description"], f"{l['amount']:,.2f}") for l in inv_lines(x["ap_doc_id"])],
        [("סה״כ לפני מע״מ", money(x["amount_before_vat"])), ("מע״מ 18%", money(x["vat_amount"])), ("סה״כ לתשלום", money(x["total"]))],
        foot="חשבונית מעל סף חובת מספר הקצאה (₪10,000 בינואר–מאי 2026). בלי מספר הקצאה מע״מ התשומות אינו ניתן לקיזוז"))
    x = find_inv("partner", issue_date="2026-10-20")
    tl = [t for t in TEL if t["billing_month"] == "2026-10"]
    dep = {e["phone_line_id"] for e in phone_departed}
    row = lambda t: (("!" if t["line_id"] in dep else "") + t["line_id"], t["plan"], t["minutes"], t["data_gb"], f"{t['total']:,.2f}")
    rows = [row(t) for t in tl if t["line_id"] not in dep][:10] + [row(t) for t in tl if t["line_id"] in dep][:4]
    out.append(receipt("receipt_partner_2026-10.html", "חשבונית מס, חשבון תקופתי", "#00a9b7", "partner", "פרטנר תקשורת · לקוחות עסקיים",
        [("לקוח", TH), ("מספר חשבון", "BA-7730152"), ("תקופת חיוב", "01/10/2026–31/10/2026"), ("מספר חשבונית", x["invoice_number"]),
         ("מספר קווים", str(len(tl))), ("מספר הקצאה", x["allocation_number"] or "—")],
        ["קו", "מסלול", "דקות", "GB", "סה״כ ₪"], rows,
        [("סה״כ לפני מע״מ", money(x["amount_before_vat"])), ("מע״מ 18%", money(x["vat_amount"])), ("סה״כ לתשלום", money(x["total"]))],
        foot="שורות מסומנות: קווים ללא שימוש 60+ יום של עובדים שסיימו העסקה. מוצגות 14 שורות מתוך הפירוט"))
    u = next(u_ for u_ in UTIL if u_["billing_period"] == "2026-10")
    prev = next(u_ for u_ in UTIL if u_["billing_period"] == "2025-10")
    out.append(receipt("receipt_iec_2026-10.html", "חשבון חשמל", "#e4002b", "חברת החשמל", "חברת החשמל לישראל · חשבון לעסקים",
        [("לקוח", TH), ("חשבון חוזה", u["contract_account"]), ("מונה", u["meter_id"]), ("תקופה", f"{u['period_start']} – {u['period_end']}"),
         ("תעריף", u["tariff"] + " (לא תעו״ז)"), ("!צריכה", f"{u['kwh']:,} קוט״ש (אשתקד {prev['kwh']:,})")],
        ["רכיב", "כמות", "תעריף", "סכום ₪"],
        [("צריכת חשמל", f"{u['kwh']:,}", u["kwh_rate"], f"{u['kwh_charge']:,.2f}"), ("תשלום קבוע וקיבולת", 1, "", f"{u['fixed_charge']:,.2f}")],
        [("סה״כ לפני מע״מ", money(u["subtotal"])), ("מע״מ 18%", money(u["vat"])), ("סה״כ לתשלום", money(u["total"]))]))
    c = next(c_ for c_ in CARS if c_["employee_id"] == EMP_CAR and c_["billing_month"] == "2026-09")
    x = next(i for i in INVOICES if i["vendor_id"] == VBY["albar"]["vendor_id"] and i["issue_date"] == "2026-09-01"
             and c["plate_masked"] in inv_lines(i["ap_doc_id"])[0]["description"])
    out.append(receipt("receipt_albar_2026-09.html", f"חשבונית מס {x['invoice_number']}", "#0055a5", "אלבר", "אלבר ציי רכב · ליסינג תפעולי",
        [("לקוח", TH), ("רכב", f"{c['plate_masked']} · {c['model']}"), ("נהג/ת", c["employee_id"]), ("חודש חיוב", "09/2026"),
         ("!תאריך החזרת רכב", c["returned_date"]), ("ק״מ בחודש", str(c["km"]))],
        ["תיאור", "סכום ₪"], [(l["description"], f"{l['amount']:,.2f}") for l in inv_lines(x["ap_doc_id"])],
        [("סה״כ לפני מע״מ", money(x["amount_before_vat"])), ("מע״מ 18%", money(x["vat_amount"])), ("סה״כ", money(x["total"]))],
        foot=f"מספר הקצאה {x['allocation_number'] or '—'}"))
    x = next(i for i in INVOICES if i["invoice_number"] == "INV-ATL-88213")
    out.append(receipt("receipt_mongodb_INV-ATL-88213.html", "Invoice", "#00684a", "MongoDB.", "MongoDB, Inc. · New York, NY · Atlas",
        [("Invoice", x["invoice_number"]), ("Invoice date", x["issue_date"]), ("Organization", "technosis-prod"), ("Period", "Jul 1 – Jul 31, 2026"),
         ("Payment method", "Card on file •••• 4417 (auto-charge)"), ("!Status", "PAID, charged 2026-08-03")],
        ["Description", "Amount (USD)"], [(l["description"], f"{l['amount']:,.2f}") for l in inv_lines(x["ap_doc_id"])],
        [("Subtotal", money(10450, "USD")), ("Total", money(10450, "USD")), ("Amount due", "$0.00")], rtl=False,
        foot="This invoice was auto-charged to the card on file"))
    x = find_inv("hubspot", issue_date="2026-10-01")
    out.append(receipt("receipt_hubspot_2026-10.html", "Renewal invoice", "#ff7a59", "HubSpot", "HubSpot Ireland Ltd · Dublin",
        [("Invoice", x["invoice_number"]), ("Date", x["issue_date"]), ("Term", "Oct 1, 2026 – Sep 30, 2027 (auto-renewed)"),
         ("!Previous term", "₪140,000.00"), ("Seats", "14 (unchanged)"), ("Currency", "ILS")],
        ["Product", "Qty", "Unit", "Amount (ILS)"],
        [(l["description"], l["quantity"], f"{l['unit_price']:,.2f}", f"{l['amount']:,.2f}") for l in inv_lines(x["ap_doc_id"])],
        [("Subtotal", money(x["amount_before_vat"])), ("VAT (reverse charge)", "₪0.00"), ("Total", money(x["total"]))], rtl=False))
    cs = [c_ for c_ in CARD if c_["card_last4"] == "4417" and c_["transaction_date"][:7] == "2026-08"]
    out.append(receipt("receipt_cal_2026-08.html", "פירוט חיובים, כרטיס עסקי", "#0072ce", "כאל", "Cal Business · פירוט חודשי",
        [("מחזיק/ת כרטיס", "EMP-1002"), ("כרטיס", "•••• 4417"), ("מועד חיוב", "10/09/2026"), ("עסקאות", str(len(cs)))],
        ["תאריך", "בית עסק", "סכום מקורי", "חיוב ₪", "עמלה ₪"],
        [(("!" if c_["merchant"] == "MONGODB CLOUD" and c_["original_amount"] == 10450 else "") + c_["transaction_date"], c_["merchant"],
          f"{c_['original_amount']:,.2f} {c_['original_currency']}", f"{c_['charged_ils']:,.2f}", f"{c_['fx_fee_ils']:,.2f}") for c_ in cs],
        [("סה״כ חיובים", money(sum(c_["charged_ils"] for c_ in cs))), ("עמלות עסקה בחו״ל", money(sum(c_["fx_fee_ils"] for c_ in cs))),
         ("סה״כ לחיוב", money(sum(c_["charged_ils"] + c_["fx_fee_ils"] for c_ in cs)))], foot="עמלת עסקה במטבע חוץ 2.5%"))
    p_ = next(p for p in PAYROLL if p["employee_id"] == EMP_POST and p["period"] == "2026-10")
    e_ = emps[EMP_POST]
    out.append(receipt("receipt_payslip_EMP-1047_2026-10.html", "תלוש שכר 10/2026", "#6b3fa0", "תלוש שכר", "טכנוסיס בע״מ · מערכת השכר",
        [("עובד/ת", f"{EMP_POST} · {e_['first_name']}"), ("מחלקה", e_["department"]), ("תחילת עבודה", e_["start_date"]),
         ("!תאריך סיום (HiBob)", e_["end_date"]), ("תאריך תשלום", p_["payment_date"]), ("חשבון בנק", p_["bank_account_hash"] + " (hash)")],
        ["רכיב", "סכום ₪"],
        [("שכר יסוד", f"{p_['base_salary']:,.2f}"), ("ברוטו", f"{p_['gross']:,.2f}"), ("מס הכנסה", f"-{p_['income_tax']:,.2f}"),
         ("ביטוח לאומי ובריאות", f"-{p_['bituach_leumi_employee']:,.2f}"), ("פנסיה עובד 6%", f"-{p_['pension_employee']:,.2f}"),
         ("קרן השתלמות עובד", f"-{p_['keren_hishtalmut_employee']:,.2f}"),
         ("הפרשות מעביד (פנסיה, פיצויים, השתלמות, ב״ל)", f"{p_['total_employer_cost'] - p_['gross']:,.2f}")],
        [("נטו לתשלום", money(p_["net"])), ("עלות מעביד", money(p_["total_employer_cost"]))]))
    nc_ = next(c_ for c_ in CARD if c_["merchant"] == "NOTION LABS, INC." and c_["transaction_date"] == "2026-05-12")
    out.append(receipt("receipt_notion_2026-05.html", "Receipt", "#111111", "Notion", "Notion Labs, Inc. · San Francisco, CA",
        [("Receipt #", "2147-8841"), ("Date paid", "May 12, 2026"), ("Plan", "Plus, annual"), ("Payment", "Visa •••• 8812"),
         ("Billing period", "May 12, 2026 – May 11, 2027"), ("Workspace", "technosis")],
        ["Description", "Qty", "Unit", "Amount (USD)"], [("Notion Plus (annual)", 32, "120.00", f"{nc_['original_amount']:,.2f}")],
        [("Subtotal", money(nc_["original_amount"], "USD")), ("Amount paid", money(nc_["original_amount"], "USD"))], rtl=False))
    return out


def shoot(files):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed, skipped PNGs"); return
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 900, "height": 300})
        for f in files:
            pg.goto((OUT / "receipts" / f).as_uri())
            pg.screenshot(path=str(OUT / "receipts" / f.replace(".html", ".png")), full_page=True)
        b.close()


# ════════════════════════════ 13. README ════════════════════════════
FORMATS = {
 "employees.csv": ("ייצוא עובדים בסגנון HiBob", "עובד לשורה כולל 23 שעזבו. שם פרטי בלבד, חשבון בנק כ-hash"),
 "payroll.csv": ("תלוש שכר ישראלי (רכיבים כמו בחילן)", "עובד × חודש: ברוטו, הפרשות מעביד 6.5%/8.33%/7.5%, ב״ל מדורג, מס, נטו"),
 "vendors.csv": ("כרטיס ספק ב-Priority ERP", "140 ספקים: ענן/SaaS/AI אמיתיים + ספקים מקומיים. משרדי עו״ד/רו״ח/ייעוץ בדויים"),
 "invoices.csv": ("כותרות חשבוניות ספקים (AP), שדות חשבונית מס", "מספר הקצאה, מע״מ 17%/18%, הזמנת רכש, סטטוס ותשלום"),
 "invoice_lines.csv": ("שורות חשבונית", "AWS לפי שירות, Datadog לפי רכיב, פרטנר לפי קו, אלבר/פז לפי רכב"),
 "bank_transactions.csv": ("דף חשבון עסקי בסגנון בנק לאומי (ILS + USD)", "תאריך, תאריך ערך, תיאור, אסמכתא, חובה, זכות, יתרה"),
 "card_transactions.csv": ("פירוט כרטיס Cal Business", "סכום מקורי, מטבע, חיוב בש״ח, עמלת עסקה בחו״ל 2.5%, מועד חיוב"),
 "aws_cur.csv": ("AWS Cost & Usage Report 2.0, יומי", "line_item_*, pricing_term, תגיות env/team/owner/cluster"),
 "ai_usage.csv": ("OpenAI usage export + Anthropic Console usage, יומי", "פרויקט, מפתח API, בעלים, מודל, טוקנים (כולל cached), עלות $ משוערת"),
 "saas_seats.csv": ("תמונת מצב חודשית של מושבי SaaS (כמו Torii/Productiv)", "כלי × משתמש: סוג מושב, מחיר, פעילות אחרונה, פעולות ב-30 יום"),
 "telecom.csv": ("חשבון פרטנר עסקים, פירוט לפי קו", "מספר מוסתר 05X-XXX-1234, מסלול, דקות, GB, נדידה"),
 "utilities.csv": ("חשבון חשמל חודשי של חברת החשמל", "קוט״ש, תעריף כללי, תשלום קבוע, מע״מ"),
 "car_leases.csv": ("חיובי ליסינג אלבר + כרטיס דלק פז", "רכב × חודש: לוחית מוסתרת, דגם, ליסינג, דלק, ק״מ, תאריך החזרה"),
}


def build_readme(counts, receipts):
    sizes = {f: (OUT / f).stat().st_size for f in counts}
    rows = "\n".join(f"| `{f}` | {FORMATS[f][0]} | {FORMATS[f][1]} | {counts[f]:,} | {sizes[f] / 1024:,.0f} KB |" for f in counts)
    plants = "\n".join(f"| {g_['finding_id']} | `{g_['rule_id']}` | ₪{g_['expected_amount_ils']:,} | {g_['kind']} | {', '.join(g_['files'])} | {g_['how']} |" for g_ in GT)
    noise = "\n".join(f"| `{n['trap']}` | {n['why']} |" for n in NOISE)
    rec = "\n".join(f"- `receipts/{r_}` + `{r_.replace('.html', '.png')}`" for r_ in receipts)
    txt = f"""# data/startup: נתוני הוצאות סינתטיים של טכנוסיס בע״מ

> **כל הנתונים סינתטיים.** החברה, העובדים, החשבוניות, חשבונות הבנק, מספרי הטלפון והסכומים בדויים לחלוטין.
> שמות ספקי הענן/SaaS/AI הם שירותים אמיתיים כדי שהדוגמה תהיה מוחשית, אבל כל עסקה וסכום מומצאים.
> משרדי עורכי הדין, רואי החשבון והייעוץ (שמיר-כהן, ברגר-אלון, קוד-פלוס וכו׳) בדויים. אין כאן מידע אישי אמיתי.

**החברה:** טכנוסיס בע״מ, סטארט-אפ Series B בתל אביב. 112 עובדים היום, 23 עזבו בתקופה.
**תקופה:** 01/11/2024 עד 31/10/2026 (24 חודשים). **שער:** USD/ILS סביב 3.70 עם תנודה קלה; כל סכום "שנתי" בממצאים מחושב לפי 3.70.
**מע״מ:** 17% עד 31/12/2024, 18% מ-01/01/2025. **מספר הקצאה:** חובה מעל ₪25,000 (2024), ₪20,000 (2025), ₪10,000 (01–05/2026), ₪5,000 (מ-06/2026), לפני מע״מ. ספקים זרים פטורים.
**מקור אמת:** `design/v2/assets/demo-data.js`. 26 הממצאים F-1001..F-1026 נשתלו בנתונים בסכומים שלו (±3%).

## הרצה

```bash
python scripts/generate_startup_data.py          # כותב את כל data/startup (דטרמיניסטי, seed 42)
python scripts/generate_startup_data.py --no-png # בלי צילומי מסך של הקבלות
python scripts/check_startup_data.py             # מחשב מחדש כל ממצא מהשורות הגולמיות ובודק ±3%
```

## קבצים

כל ה-CSV ב-UTF-8 עם BOM (אקסל מציג עברית), כותרות באנגלית snake_case.

| קובץ | מחקה את הפורמט של | תוכן | שורות | גודל |
|---|---|---|---:|---:|
{rows}
| **סה״כ** | | | **{sum(counts.values()):,}** | |

`ground_truth.json`: רשימת הממצאים שנשתלו (מזהה, כלל, קבצים ומפתחות שורה שמוכיחים, סכום צפוי) ורשימת מלכודות הרעש.

## 26 הממצאים שנשתלו

| ממצא | כלל | סכום DEMO | סוג | קבצים | איך מזהים ואיך מחושב הסכום |
|---|---|---:|---|---|---|
{plants}


## מלכודות רעש (אסור שיסומנו)

| מלכודת | למה זה תקין |
|---|---|
{noise}

## מסמכים לדוגמה

12 קבלות וחשבוניות HTML שתואמות שורות בנתונים, עם סימן מים "SYNTHETIC · דוגמה" ובלי לוגואים אמיתיים (שם טקסטואלי בלבד), וצילום PNG ברוחב 900px לכל אחת:

{rec}

## פישוטים ידועים

- מחירי הטוקנים ב-`ai_usage.csv` הם **מחירון ציבורי משוער** ל-1M טוקנים (gpt-5 $1.25/$10, claude-opus-4-5 $5/$25 וכו׳), לא חשבון אמיתי.
- תעריפי AWS ב-CUR משוערים (eu-central-1) וחלקם מכוילים כדי שהממצאים ייצאו בסכום של ה-DEMO. שורות Savings Plan מוצגות בעלות האפקטיבית, בלי שורת SavingsPlanRecurringFee נפרדת.
- התגיות ב-CUR שטוחות (`resource_tags_user_env`) כמו ב-CUR הוותיק, במקום עמודת המפה `resource_tags` של CUR 2.0.
- תעריף החשמל (כ-0.43 ₪ לקוט״ש לפני מע״מ) ותשלום הקיבולת הקבוע משוערים.
- מס הכנסה וביטוח לאומי בתלוש מחושבים בקירוב לפי מדרגות 2025 (2.25 נקודות זיכוי, בלי תקרות הפקדה). מספיק לסדר גודל של נטו.
- כמה פרטים בטקסט ה-DEMO לא מתיישבים עם המחירון ולכן הותאמו: ב-F-1001 יש כ-480 אלף קריאות בחודש (לא 2.1M) כדי שעלות מודל הדגל תתאים ל-₪214K; ב-F-1007 נספרו 4.73M קריאות ב-12 חודשים, 92% מהן עם ה-prefix. סכומי חלק מהספקים בטבלת ה-vendors של ה-DEMO (חשמל, monday) שונים מעט מהנתונים.
"""
    (OUT / "README.md").write_text(txt, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    rec = build_receipts()
    if "--no-png" not in sys.argv: shoot(rec)
    build_readme(counts, rec)
    print(f"wrote {OUT}  total rows: {sum(counts.values()):,}  receipts: {len(rec)}")
    for k, v in counts.items(): print(f"  {k:24s} {v:>8,}")
