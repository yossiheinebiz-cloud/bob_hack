# -*- coding: utf-8 -*-
"""scripts/export_findings.py — מריץ מנוע ומייצא ממצאים ל-JSON לדשבורד"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, ".")

import pandas as pd
from pathlib import Path
from datetime import date, datetime
from engine.rules import ALL_SINGLE_TABLE_RULES, ALL_MULTI_TABLE_RULES

def json_serial(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Not serializable: {type(obj)}")

DATA = Path("data/synthetic")
OUT  = Path("dashboard/findings.json")

tables = {f.stem: pd.read_csv(f) for f in DATA.glob("*.csv")}
findings = []

for rule_name, rule_fn, table_name in ALL_SINGLE_TABLE_RULES:
    if table_name in tables:
        for f in rule_fn(tables[table_name]):
            findings.append({**f.to_dict(), "evidence": f.evidence[:3]})

for rule_name, rule_fn, table_names in ALL_MULTI_TABLE_RULES:
    if all(t in tables for t in table_names):
        for f in rule_fn(*[tables[t] for t in table_names]):
            findings.append({**f.to_dict(), "evidence": f.evidence[:3]})

# מיין לפי כסף
findings.sort(key=lambda x: x["amount_at_risk"], reverse=True)

# הוסף IDs
for i, f in enumerate(findings, 1):
    f["finding_id"] = f"F{i:03d}"

total = sum(f["amount_at_risk"] for f in findings)
by_cat = {}
for f in findings:
    by_cat[f["category"]] = by_cat.get(f["category"], 0) + f["amount_at_risk"]

payload = {
    "company": "טכנוסיס בע\"מ",
    "generated_at": "2026-11-01T12:00:00",
    "total_at_risk": total,
    "findings_count": len(findings),
    "by_category": by_cat,
    "findings": findings
}

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=json_serial), encoding="utf-8")
print(f"✅ {len(findings)} ממצאים → {OUT}  |  סה\"כ: ₪{total:,.0f}")
