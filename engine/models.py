"""
engine/models.py — מבנה הנתונים המשותף לכל הכלי

Finding: ממצא אחד שמנוע הכללים מחזיר.
כל כלל מחזיר list[Finding].
"""
from dataclasses import dataclass, field
from typing import Literal
from datetime import datetime


@dataclass
class Finding:
    rule_id: str                    # "DUP_INVOICE_EXACT"
    title: str                      # "חשבונית כפולה — מילגם בע״מ"
    amount_at_risk: float           # ₪ בסיכון (שנתי)
    confidence: float               # 0.0–1.0
    evidence: list[dict]            # השורות המקוריות שהפעילו את הכלל
    action: str                     # "פנה לספק לקבלת זיכוי"
    category: str = "general"       # "duplicates"|"payroll"|"licenses"|"cloud"
    domain: str = "hitech"          # "hitech"|"org"|"public"|"startup"
    status: Literal[
        "open", "in_progress", "reviewed_ok", "fixed"
    ] = "open"
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    finding_id: str = ""            # נוצר ב-scorer.py

    def to_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "rule_id": self.rule_id,
            "title": self.title,
            "amount_at_risk": self.amount_at_risk,
            "confidence": self.confidence,
            "category": self.category,
            "domain": self.domain,
            "action": self.action,
            "status": self.status,
            "created_at": self.created_at,
            "evidence_count": len(self.evidence),
        }


@dataclass
class Dataset:
    dataset_id: str
    company_name: str
    domain: str
    uploaded_at: str
    files: list[str]
    row_counts: dict[str, int]
    findings: list[Finding] = field(default_factory=list)

    @property
    def total_at_risk(self) -> float:
        return sum(f.amount_at_risk for f in self.findings if f.status == "open")

    @property
    def open_findings(self) -> list[Finding]:
        return [f for f in self.findings if f.status == "open"]
