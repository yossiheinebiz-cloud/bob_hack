# -*- coding: utf-8 -*-
"""
api/main.py — FastAPI backend for איפה הכסף
Run: uvicorn api.main:app --reload
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal, Optional
import pandas as pd
import json
import io
import uuid
from datetime import datetime
from pathlib import Path

from engine.rules import ALL_SINGLE_TABLE_RULES, ALL_MULTI_TABLE_RULES
from engine.models import Finding

app = FastAPI(
    title="איפה הכסף — API",
    description="Financial waste detection engine for Israeli hi-tech companies",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory state (demo only — replace with DB in prod) ────────────────────
_findings: list[dict] = []
_last_scan: Optional[str] = None
_company: str = "טכנוסיס בע\"מ"


# ── Models ───────────────────────────────────────────────────────────────────

class StatusUpdate(BaseModel):
    status: Literal["open", "in_progress", "reviewed_ok", "fixed"]

class ScanResult(BaseModel):
    company: str
    generated_at: str
    total_at_risk: float
    findings_count: int
    by_category: dict
    findings: list[dict]


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", summary="Health check")
def root():
    return {"status": "ok", "service": "איפה הכסף", "version": "0.1.0"}


@app.get("/findings", summary="Get all findings", response_model=ScanResult)
def get_findings(
    status: Optional[str] = None,
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
):
    """Return findings with optional filters."""
    findings = _findings
    if status:
        findings = [f for f in findings if f["status"] == status]
    if category:
        findings = [f for f in findings if f["category"] == category]
    if min_amount:
        findings = [f for f in findings if f["amount_at_risk"] >= min_amount]

    total = sum(f["amount_at_risk"] for f in findings if f["status"] == "open")
    by_cat: dict[str, float] = {}
    for f in findings:
        by_cat[f["category"]] = by_cat.get(f["category"], 0) + f["amount_at_risk"]

    return ScanResult(
        company=_company,
        generated_at=_last_scan or datetime.now().isoformat(),
        total_at_risk=total,
        findings_count=len([f for f in findings if f["status"] == "open"]),
        by_category=by_cat,
        findings=findings,
    )


@app.get("/findings/{finding_id}", summary="Get a single finding")
def get_finding(finding_id: str):
    f = next((x for x in _findings if x["finding_id"] == finding_id), None)
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    return f


@app.patch("/findings/{finding_id}/status", summary="Update finding status")
def update_status(finding_id: str, body: StatusUpdate):
    f = next((x for x in _findings if x["finding_id"] == finding_id), None)
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    f["status"] = body.status
    f["updated_at"] = datetime.now().isoformat()
    return {"finding_id": finding_id, "status": body.status}


@app.post("/scan", summary="Run full scan on uploaded CSV files")
async def run_scan(
    employees:   Optional[UploadFile] = File(None),
    payroll:     Optional[UploadFile] = File(None),
    invoices:    Optional[UploadFile] = File(None),
    licenses:    Optional[UploadFile] = File(None),
    cloud_costs: Optional[UploadFile] = File(None),
):
    """
    Accept CSV uploads, run all rules, return findings.
    Any subset of files is acceptable — rules that need missing files are skipped.
    """
    global _findings, _last_scan

    tables: dict[str, pd.DataFrame] = {}

    async def read_csv(upload: Optional[UploadFile], name: str):
        if upload is None:
            return
        content = await upload.read()
        try:
            tables[name] = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse {name}: {e}")

    await read_csv(employees,   "employees")
    await read_csv(payroll,     "payroll")
    await read_csv(invoices,    "invoices")
    await read_csv(licenses,    "licenses")
    await read_csv(cloud_costs, "cloud_costs")

    if not tables:
        raise HTTPException(status_code=400, detail="No CSV files uploaded")

    all_findings: list[Finding] = []

    # Single-table rules
    for rule_name, rule_fn, table_name in ALL_SINGLE_TABLE_RULES:
        if table_name not in tables:
            continue
        try:
            found = rule_fn(tables[table_name])
            all_findings.extend(found)
        except Exception:
            pass  # rule error — skip, don't crash scan

    # Multi-table rules
    for rule_name, rule_fn, table_names in ALL_MULTI_TABLE_RULES:
        if not all(t in tables for t in table_names):
            continue
        try:
            args = [tables[t] for t in table_names]
            found = rule_fn(*args)
            all_findings.extend(found)
        except Exception:
            pass

    # Assign IDs and serialize
    result_findings = []
    for i, f in enumerate(sorted(all_findings, key=lambda x: x.amount_at_risk, reverse=True), 1):
        f.finding_id = f"F{i:03d}"
        d = f.to_dict()
        d["evidence"] = f.evidence
        result_findings.append(d)

    _findings = result_findings
    _last_scan = datetime.now().isoformat()

    total_risk = sum(f["amount_at_risk"] for f in result_findings if f["status"] == "open")
    by_cat: dict[str, float] = {}
    for f in result_findings:
        by_cat[f["category"]] = by_cat.get(f["category"], 0) + f["amount_at_risk"]

    return ScanResult(
        company=_company,
        generated_at=_last_scan,
        total_at_risk=total_risk,
        findings_count=len([f for f in result_findings if f["status"] == "open"]),
        by_category=by_cat,
        findings=result_findings,
    )


@app.post("/scan/synthetic", summary="Run scan on built-in synthetic data")
def run_synthetic_scan():
    """Run the engine on the pre-generated synthetic CSV files (demo mode)."""
    global _findings, _last_scan

    data_dir = Path("data/synthetic")
    if not data_dir.exists():
        raise HTTPException(status_code=404, detail="Synthetic data not found — run scripts/generate_data.py first")

    tables: dict[str, pd.DataFrame] = {}
    for f in data_dir.glob("*.csv"):
        tables[f.stem] = pd.read_csv(f)

    all_findings: list[Finding] = []

    for rule_name, rule_fn, table_name in ALL_SINGLE_TABLE_RULES:
        if table_name not in tables:
            continue
        try:
            all_findings.extend(rule_fn(tables[table_name]))
        except Exception:
            pass

    for rule_name, rule_fn, table_names in ALL_MULTI_TABLE_RULES:
        if not all(t in tables for t in table_names):
            continue
        try:
            all_findings.extend(rule_fn(*[tables[t] for t in table_names]))
        except Exception:
            pass

    result_findings = []
    for i, f in enumerate(sorted(all_findings, key=lambda x: x.amount_at_risk, reverse=True), 1):
        f.finding_id = f"F{i:03d}"
        d = f.to_dict()
        d["evidence"] = f.evidence
        result_findings.append(d)

    _findings = result_findings
    _last_scan = datetime.now().isoformat()

    total_risk = sum(f["amount_at_risk"] for f in result_findings if f["status"] == "open")
    by_cat: dict[str, float] = {}
    for f in result_findings:
        by_cat[f["category"]] = by_cat.get(f["category"], 0) + f["amount_at_risk"]

    return {
        "company": _company,
        "generated_at": _last_scan,
        "total_at_risk": total_risk,
        "findings_count": len([f for f in result_findings if f["status"] == "open"]),
        "by_category": by_cat,
        "findings": result_findings,
        "tables_scanned": list(tables.keys()),
        "row_counts": {k: len(v) for k, v in tables.items()},
    }


@app.get("/stats", summary="Summary statistics")
def get_stats():
    open_f  = [f for f in _findings if f["status"] == "open"]
    fixed_f = [f for f in _findings if f["status"] == "fixed"]
    return {
        "total_findings":    len(_findings),
        "open":              len(open_f),
        "fixed":             len(fixed_f),
        "total_at_risk":     sum(f["amount_at_risk"] for f in open_f),
        "total_recovered":   sum(f["amount_at_risk"] for f in fixed_f),
        "last_scan":         _last_scan,
        "categories":        list({f["category"] for f in _findings}),
    }
