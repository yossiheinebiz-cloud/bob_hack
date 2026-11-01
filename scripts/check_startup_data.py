# -*- coding: utf-8 -*-
"""
scripts/check_startup_data.py — verifies data/startup against data/startup/ground_truth.json.

For every planted finding it recomputes the ₪ amount from the RAW rows with a simple pandas query
(most queries are generic detectors, so they also prove the noise traps are NOT flagged) and asserts
it is within ±3% of the DEMO amount. It also checks last-12-month spend per category within ±10% of
DEMO.spend.byCategory and that the dataset has > 150,000 rows.

Run: python scripts/check_startup_data.py      (exit code 1 on any failure)
"""
import json, sys
from pathlib import Path
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")

P = Path(__file__).resolve().parent.parent / "data" / "startup"
FX = 3.70
L12 = ("2025-11-01", "2026-10-31")
SNAP = "2026-10-31"


def rd(name, num=()):
    df = pd.read_csv(P / name, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    for c in num: df[c] = pd.to_numeric(df[c].replace("", "0"))
    return df


emp = rd("employees.csv")
pay = rd("payroll.csv", ["total_employer_cost", "net", "gross"])
ven = rd("vendors.csv")
inv = rd("invoices.csv", ["amount_before_vat", "vat_rate", "vat_amount", "total"])
lines = rd("invoice_lines.csv", ["amount"])
bank = rd("bank_transactions.csv", ["debit", "credit"])
card = rd("card_transactions.csv", ["original_amount", "charged_ils", "fx_fee_ils"])
cur = rd("aws_cur.csv", ["line_item_unblended_cost", "line_item_usage_amount"])
ai = rd("ai_usage.csv", ["requests", "input_tokens", "cached_input_tokens", "output_tokens", "cost_usd"])
seats = rd("saas_seats.csv", ["seat_cost_usd_month", "actions_30d"])
tel = rd("telecom.csv", ["monthly_fee", "minutes", "data_gb", "roaming_charges"])
util = rd("utilities.csv", ["kwh", "kwh_rate", "kwh_charge"])
cars = rd("car_leases.csv", ["monthly_fee", "km"])
gt = json.load(open(P / "ground_truth.json", encoding="utf-8"))
END = dict(zip(emp.employee_id, emp.end_date))
cur["day"] = cur.line_item_usage_start_date.str[:10]
in12 = lambda s: (s >= L12[0]) & (s <= L12[1])
res, notes = {}, {}

# F-1001 flagship model on a classification route
r = ai[(ai.api_key_name == "ticket-classifier-prod") & (ai.model == "claude-opus-4-5") & (ai.date.str[:7] == "2026-10")]
res["F-1001"] = r.cost_usd.sum() * .8 * 12 * FX
notes["F-1001"] = f"{r.requests.sum():,} req in 10/2026, avg out {r.output_tokens.sum() / r.requests.sum():.0f} tok"

# F-1002 no commitment on stable prod On-Demand compute
ec2 = cur[(cur.line_item_product_code == "AmazonEC2") & cur.line_item_usage_type.str.contains("BoxUsage") & in12(cur.day)]
od = ec2[(ec2.pricing_term == "OnDemand") & (ec2.resource_tags_user_env == "prod")]
res["F-1002"] = od.line_item_unblended_cost.sum() * .75 * .28 * FX
notes["F-1002"] = f"On-Demand share of EC2 compute {ec2[ec2.pricing_term == 'OnDemand'].line_item_unblended_cost.sum() / ec2.line_item_unblended_cost.sum():.0%}"

# F-1003 zombie cluster: zero ALB LCU since a date, resources still billing
so = cur[cur.resource_tags_user_cluster == "staging-old"]
lcu = so[so.line_item_usage_type.str.endswith("LCUUsage")]
zero_from = lcu[lcu.line_item_usage_amount > 0].day.max()
z = so[so.day > zero_from]
res["F-1003"] = z.line_item_unblended_cost.sum() / z.day.nunique() * 365 * FX
notes["F-1003"] = f"last ALB traffic {zero_from}, {z.day.nunique()} idle days"

# F-1004 Datadog DEBUG indexed logs
dd = lines.merge(inv[["ap_doc_id", "vendor_name", "issue_date", "currency"]], on="ap_doc_id")
dbg = dd[(dd.vendor_name == "Datadog Inc") & dd.description.str.contains("status:debug") & in12(dd.issue_date)]
idx = dd[(dd.vendor_name == "Datadog Inc") & dd.description.str.contains("Indexed Logs") & in12(dd.issue_date)]
res["F-1004"] = dbg.amount.sum() * FX
notes["F-1004"] = f"DEBUG = {dbg.amount.sum() / idx.amount.sum():.0%} of indexed-log spend"

# F-1005 API key of a departed employee still consuming (generic)
last_use = ai.groupby(["api_key_name", "api_key_owner_employee_id"]).date.max().reset_index()
last_use["end"] = last_use.api_key_owner_employee_id.map(END)
orphan = last_use[(last_use.end != "") & (last_use.date > last_use.end)]
assert set(orphan.api_key_name) == {"dan-experiments"}, orphan
res["F-1005"] = ai[(ai.api_key_name == "dan-experiments") & (ai.date.str[:7] == "2026-10")].cost_usd.sum() * 12 * FX

# F-1006 dev instances always on (24h incl. Fri/Sat)
dev = ec2[ec2.resource_tags_user_env == "dev"]
wk = pd.to_datetime(dev.day).dt.weekday.isin([4, 5])
assert (dev[wk].line_item_usage_amount == 24).all()
res["F-1006"] = dev.line_item_unblended_cost.sum() * 98 / 168 * FX
notes["F-1006"] = f"{dev.line_item_resource_id.nunique()} dev instances, 24h on weekends"

# F-1007 no prompt caching
sc = ai[(ai.api_key_name == "support-copilot-prod") & in12(ai.date)]
assert sc.cached_input_tokens.sum() == 0
res["F-1007"] = sc.requests.sum() * .92 * 3200 * (1.25 - .125) / 1e6 * FX
notes["F-1007"] = f"{sc.requests.sum() / 1e6:.2f}M requests in 12m, 0 cached tokens"

# F-1008 two work-management tools
o = seats[seats.snapshot_date == SNAP]
both = set(o[o.tool == "jira"].employee_id) & set(o[o.tool == "monday"].employee_id)
res["F-1008"] = card[(card.merchant == "MONDAY.COM") & in12(card.transaction_date)].charged_ils.sum()
notes["F-1008"] = f"jira {len(o[o.tool == 'jira'])} / monday {len(o[o.tool == 'monday'])} users, {len(both)} in both"

# F-1009 auto-renewal price jump
hs = inv[inv.vendor_name == "HubSpot"].sort_values("issue_date")
res["F-1009"] = hs.amount_before_vat.iloc[-1] - hs.amount_before_vat.iloc[-2]

# F-1010 NAT egress spike
nat = cur[cur.line_item_usage_type.str.endswith("NatGateway-Bytes") & (cur.resource_tags_user_env == "prod")]
nat_m = nat.groupby([nat.line_item_resource_id, nat.day.str[:7]]).line_item_unblended_cost.sum()
spike = None
for rid, s in nat_m.groupby(level=0):
    s = s.droplevel(0)
    after, before = s[(s.index >= "2026-08")].mean(), s[(s.index >= "2026-01") & (s.index <= "2026-07")].mean()
    if after > 2 * before: spike = (rid, (after - before) * 12 * FX)
res["F-1010"] = spike[1]
notes["F-1010"] = f"resource {spike[0]}"

# F-1011 unused Figma editors
fg = o[(o.tool == "figma") & (o.seat_type == "editor")]
idle = fg[pd.to_datetime(fg.last_active_date) < pd.Timestamp(SNAP) - pd.Timedelta(days=90)]
res["F-1011"] = idle.seat_cost_usd_month.sum() * 12 * FX
notes["F-1011"] = f"{len(fg)} editors, {len(idle)} idle 90d+"

# F-1012 / F-1022 card + AP double payment (generic: AP invoice of a card vendor matching a card charge)
cv = ven[ven.card_descriptor != ""][["vendor_id", "card_descriptor"]]
m = inv[inv.status == "paid"].merge(cv, on="vendor_id").merge(card, left_on="card_descriptor", right_on="merchant")
m = m[(abs(m.original_amount - m.total) < .01) &
      (abs(pd.to_datetime(m.paid_date) - pd.to_datetime(m.transaction_date)).dt.days <= 14)]
assert set(m.vendor_name) == {"MongoDB Atlas", "Notion Labs"}, set(m.vendor_name)
mg = m[m.vendor_name == "MongoDB Atlas"].iloc[0]
b = bank[bank.reference == mg.payment_ref]
res["F-1012"] = b.debit.sum()
notes["F-1012"] = f"{mg.invoice_number}: card ${mg.original_amount:,.0f} {mg.transaction_date} + bank {b.currency.iloc[0]} {b.debit.sum():,.0f} {b.date.iloc[0]}"
nt = m[m.vendor_name == "Notion Labs"].iloc[0]
res["F-1022"] = nt.charged_ils
notes["F-1022"] = f"card {nt.transaction_date}, AP paid {nt.paid_date}"

# F-1013 orphaned EBS (source instance not running in the last 60 days)
live = set(cur[cur.line_item_usage_type.str.contains("BoxUsage") & (cur.day >= "2026-09-01")].line_item_resource_id)
ebs = cur[cur.line_item_usage_type.str.contains("EBS:") & (cur.day.str[:7] == "2026-10")]
orph = ebs[~ebs.resource_tags_user_source_instance.isin(live)]
res["F-1013"] = orph.line_item_unblended_cost.sum() * 12 * FX
notes["F-1013"] = f"{orph[orph.line_item_resource_id.str.startswith('vol-')].line_item_resource_id.nunique()} volumes + {orph[orph.line_item_resource_id.str.startswith('snap-')].line_item_resource_id.nunique()} snapshots"

# F-1014 payslip after termination (generic)
pay["end"] = pay.employee_id.map(END)
post = pay[(pay.end != "") & (pay.period > pay.end.str[:7])]
assert list(post.employee_id) == ["EMP-1047"], post
res["F-1014"] = post.total_employer_cost.sum()

# F-1015 departed employees holding seats (generic)
o2 = o.assign(end=o.employee_id.map(END))
dep = o2[(o2.end != "") & (o2.end < SNAP)]
res["F-1015"] = dep.seat_cost_usd_month.sum() * 12 * FX
notes["F-1015"] = f"{dep.employee_id.nunique()} employees, tools {sorted(dep.tool.unique())}"

# F-1016 FX fees on USD card charges
c12 = card[in12(card.transaction_date)]
res["F-1016"] = c12.fx_fee_ils.sum()
notes["F-1016"] = f"USD card volume ₪{c12[c12.original_currency == 'USD'].charged_ils.sum():,.0f}"

# F-1017 exact duplicate invoice (generic, cancelled excluded)
act = inv[inv.status != "cancelled"]
dup = act[act.duplicated(["vendor_id", "invoice_number"], keep=False)]
assert set(dup.invoice_number) == {"2026-0412"}, set(dup.invoice_number)
res["F-1017"] = dup.total.iloc[0]
notes["F-1017"] = f"paid {sorted(dup.paid_date)}"

# F-1018 Cursor active + Copilot unused
cu = set(o[(o.tool == "cursor") & (o.actions_30d > 0)].employee_id)
cp = o[(o.tool == "copilot") & (o.actions_30d == 0) & o.employee_id.isin(cu)]
res["F-1018"] = cp.seat_cost_usd_month.sum() * 12 * FX
notes["F-1018"] = f"{len(cp)} overlapping users"

# F-1019 shared bank account (generic, active employees)
a = emp[emp.end_date == ""]
sh = a[a.duplicated("bank_account_hash", keep=False)]
assert set(sh.employee_id) == {"EMP-1033", "EMP-1088"}, sh
res["F-1019"] = pay[(pay.employee_id == "EMP-1088") & (pay.period == "2026-10")].net.sum()

# F-1020 missing allocation number (generic, threshold by issue date)
def thr(d): return 25000 if d < "2025-01-01" else 20000 if d < "2026-01-01" else 10000 if d < "2026-06-01" else 5000
il = act[(act.currency == "ILS") & (act.vat_rate > 0)]
na = il[(il.amount_before_vat > il.issue_date.map(thr)) & (il.allocation_number == "")]
res["F-1020"] = na.vat_amount.sum()
notes["F-1020"] = f"{len(na)} invoices, {na.vendor_name.nunique()} vendors"

# F-1021 electricity spike (generic YoY > 25%)
u = util.set_index("billing_period")
yoy = {p: u.kwh[p] / u.kwh[f"{int(p[:4]) - 1}{p[4:]}"] for p in u.index if p >= "2025-11"}
spk = [p for p, v in yoy.items() if v > 1.25]
assert spk == ["2026-09", "2026-10"], yoy
res["F-1021"] = sum((u.kwh[p] - u.kwh[f"{int(p[:4]) - 1}{p[4:]}"]) * u.kwh_rate[p] for p in spk) * 6
notes["F-1021"] = f"YoY Aug-2026 {yoy['2026-08']:.2f} (seasonal, not flagged), Sep {yoy['2026-09']:.2f}"

# F-1023 lease charged after car return (generic)
cr = cars[(cars.returned_date != "") & (cars.billing_month > cars.returned_date.str[:7])]
assert set(cr.employee_id) == {"EMP-1019"}, cr
res["F-1023"] = cr.monthly_fee.sum()

# F-1024 lines of departed employees, no usage 60d+ (generic)
t = tel.assign(end=tel.employee_id.map(END))
recent = t[t.billing_month.isin(["2026-09", "2026-10"])].groupby("line_id")[["minutes", "data_gb"]].sum()
dead = recent[(recent.minutes == 0) & (recent.data_gb == 0)].index
tl = t[(t.billing_month == "2026-10") & t.line_id.isin(dead) & (t.end != "")]
res["F-1024"] = tl.monthly_fee.sum() * 12
notes["F-1024"] = f"{len(tl)} lines"

# F-1025 per-use roaming without abroad package
ro = tel[(tel.plan == "עסקי 89") & (tel.roaming_charges > 0)]
res["F-1025"] = ro[ro.billing_month >= "2025-11"].roaming_charges.sum()
notes["F-1025"] = f"{ro.line_id.nunique()} lines"

# F-1026 invoice splitting (generic: >=3 invoices of one vendor within 30 days, each 85–100% of the ₪20,000 threshold)
band = act[(act.currency == "ILS") & (act.amount_before_vat >= 17000) & (act.amount_before_vat < 20000)].copy()
band["d"] = pd.to_datetime(band.issue_date)
hits = []
for vid, g in band.groupby("vendor_id"):
    g = g.sort_values("d")
    for k in range(len(g)):
        w = g[(g.d >= g.d.iloc[k]) & (g.d <= g.d.iloc[k] + pd.Timedelta(days=30))]
        if len(w) >= 3: hits.append(w); break
assert len(hits) == 1 and hits[0].vendor_name.iloc[0] == "קוד-פלוס ייעוץ", [h.vendor_name.iloc[0] for h in hits]
res["F-1026"] = hits[0].amount_before_vat.sum()
notes["F-1026"] = f"{len(hits[0])} invoices, {(hits[0].d.max() - hits[0].d.min()).days} days"

# ── noise traps that the generic queries above did not already cover
noise = {}
# sub-₪200 micro-charges (parking) collide by chance, a duplicate detector ignores them
cc = card[card.charged_ils >= 200].copy(); cc["d"] = pd.to_datetime(cc.transaction_date)
near = cc.merge(cc, on=["merchant", "original_amount"])
near = near[(near.voucher_x < near.voucher_y) & ((near.d_x - near.d_y).abs().dt.days <= 3)]
noise["card ≥₪200: same merchant+amount within 3 days (recurring/refund)"] = len(near) == 0
noise["refund row present (negative charged_ils)"] = (card.charged_ils < 0).sum() >= 1
noise["cancelled invoice kept but excluded"] = (inv.status == "cancelled").sum() >= 1

# ── report
ok = True
print(f"{'id':7} {'rule':26} {'expected ₪':>12} {'recomputed ₪':>13} {'diff':>7}  result  evidence")
for f in gt["planted"]:
    fid, exp = f["finding_id"], f["expected_amount_ils"]
    got = float(res[fid]); d = got / exp - 1
    good = abs(d) <= .03
    ok &= good
    print(f"{fid:7} {f['rule_id']:26} {exp:>12,.0f} {got:>13,.0f} {d:>+7.1%}  {'PASS' if good else 'FAIL'}    {notes.get(fid, '')}")

DEMO = {"payroll": 55_200_000, "cloud": 6_100_000, "saas": 3_400_000, "office": 2_600_000, "ai": 1_900_000, "ap": 1_200_000, "finance": 700_000, "telecom": 300_000}
cat = ven.set_index("vendor_id").category
i12 = act[in12(act.issue_date)]
spend = (i12.amount_before_vat * i12.currency.map({"USD": FX, "ILS": 1})).groupby(i12.vendor_id.map(cat)).sum()
cmap = ven[ven.card_descriptor != ""].set_index("card_descriptor").category
spend = spend.add(c12.charged_ils.groupby(c12.merchant.map(cmap)).sum(), fill_value=0)
b12 = bank[in12(bank.date) & bank.description.str.startswith(("עמלות", "עמלת", "SWIFT fees"))]
fees = (b12.debit * b12.currency.map({"USD": FX, "ILS": 1})).sum()
spend["finance"] += c12.fx_fee_ils.sum() + fees
spend["payroll"] += pay[pay.period >= "2025-11"].total_employer_cost.sum()
print(f"\n{'category':10} {'DEMO ₪':>12} {'data ₪ (11/25–10/26)':>22} {'diff':>7}")
for k, v in DEMO.items():
    d = spend.get(k, 0) / v - 1
    good = abs(d) <= .10; ok &= good
    print(f"{k:10} {v:>12,.0f} {spend.get(k, 0):>22,.0f} {d:>+7.1%}  {'PASS' if good else 'FAIL'}")
print()
for k, v in noise.items():
    ok &= bool(v); print(f"noise: {k:62} {'PASS' if v else 'FAIL'}")
n = sum(len(pd.read_csv(P / f, encoding="utf-8-sig", usecols=[0])) for f in gt["row_counts"])
ok &= n > 150_000
print(f"total rows: {n:,} {'PASS' if n > 150_000 else 'FAIL'} (> 150,000)")
print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED")
sys.exit(0 if ok else 1)
