# -*- coding: utf-8 -*-
"""
scripts/run_engine.py
מריץ את כל הכללים על data/synthetic/ ומדפיס ממצאים.
הרץ: python scripts/run_engine.py
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, ".")

import pandas as pd
from pathlib import Path
from engine.rules import ALL_SINGLE_TABLE_RULES, ALL_MULTI_TABLE_RULES

DATA = Path("data/synthetic")

# טען קבצים
tables = {}
for f in DATA.glob("*.csv"):
    tables[f.stem] = pd.read_csv(f)
    print(f"  טעינה: {f.stem} ({len(tables[f.stem])} שורות)")

print("\n" + "="*60)
print("מריץ כללים...")
print("="*60)

all_findings = []

# כללים על טבלה אחת
for rule_name, rule_fn, table_name in ALL_SINGLE_TABLE_RULES:
    if table_name not in tables:
        print(f"  [SKIP] {rule_name} — חסר קובץ {table_name}")
        continue
    findings = rule_fn(tables[table_name])
    all_findings.extend(findings)
    print(f"  {rule_name:<35} {len(findings):>3} ממצאים")

# כללים על כמה טבלאות
for rule_name, rule_fn, table_names in ALL_MULTI_TABLE_RULES:
    if not all(t in tables for t in table_names):
        missing = [t for t in table_names if t not in tables]
        print(f"  [SKIP] {rule_name} — חסרים: {missing}")
        continue
    args = [tables[t] for t in table_names]
    findings = rule_fn(*args)
    all_findings.extend(findings)
    print(f"  {rule_name:<35} {len(findings):>3} ממצאים")

# סיכום
print("\n" + "="*60)
print(f"סה\"כ ממצאים: {len(all_findings)}")
total_risk = sum(f.amount_at_risk for f in all_findings)
print(f"סה\"כ כסף בסיכון: {total_risk:,.0f}")
print("="*60)

if all_findings:
    print("\nממצאים לפי גודל:")
    for i, f in enumerate(sorted(all_findings, key=lambda x: x.amount_at_risk, reverse=True), 1):
        bar = "█" * min(40, int(f.amount_at_risk / total_risk * 40))
        print(f"  {i:>2}. [{f.confidence:.0%}] {f.title:<50} {f.amount_at_risk:>10,.0f} {bar}")
