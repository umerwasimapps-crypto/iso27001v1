"""Helpers to manage readiness table statuses."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATUS_FILE = PROJECT_ROOT / "memory" / "readiness_status.json"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

TASK_ORDER = [
    "Determine Internal and External Issues",
    "Determine Interested Parties",
    "Determine certification scope",
    "Establish organisational processes",
    "Establish an Information Security Policy",
    "Establish roles and responsibilities",
    "Determine business risks and opportunities",
    "Determine information security legal obligations",
    "Establish Information Security Objectives",
    "Establish infrastructure and asset maintenance schedules",
    "Establish employee competence and skills management",
    "Establish and manage communications",
    "Establish control of documentation",
    "Establish supplier management processes",
    "Establish an internal audit plan",
    "Capturing internal audit results",
    "Define and capture management review meeting minutes",
    "Establish how non conformities, risks, and opportunities are captured",
    "Establish an Acceptable Use of Assets Policy",
    "Establish an Access Control Policy",
    "Establish a Backup Policy",
    "Establish a Clear Desk and Clear Screen Policy",
    "Establish a Configuration Management Policy",
    "Establish a Cryptographic Controls Policy",
    "Establish an Information Classification, Labelling, and Handling Policy",
    "Establish a Mobile Devices Policy",
    "Establish an Operational Controls Policy",
    "Establish a Physical and Environmental Security Policy",
    "Establish a Protection from Malware Policy",
    "Establish a Protection of Personal Information Policy",
    "Establish a Remote Working Policy",
    "Establish a Supplier Policy",
    "Establish a Threat Intelligence Policy",
    "Establish a Use of Intellectual Property Policy",
    "Establish a Use of Software Policy",
    "Establish an information security incident response process",
    "Establish an information security change management process",
    "Determine credible business continuity disruption events and analyse their impact",
    "Establish screening checks",
    "Establish appropriate terms and conditions of employment",
    "Establish a formal disciplinary process",
    "Establish confidentiality or non-disclosure agreements",
    "Establish an Information Asset Register",
    "Establish an information security risk assessment criteria",
    "Determine and assess information security risks",
    "Establish and maintain risk treatment plans",
    "Create a Statement of Applicability",
]

CONSULTANT_TASKS = TASK_ORDER[:18]
ASSET_TASKS = ["Establish an Information Asset Register"]
RISK_TASKS = [
    "Establish an information security risk assessment criteria",
    "Determine and assess information security risks",
    "Determine credible business continuity disruption events and analyse their impact",
]
TREATMENT_TASKS = ["Establish and maintain risk treatment plans"]
POLICY_TASKS = [
    "Establish an Acceptable Use of Assets Policy",
    "Establish an Access Control Policy",
    "Establish a Backup Policy",
    "Establish a Clear Desk and Clear Screen Policy",
    "Establish a Configuration Management Policy",
    "Establish a Cryptographic Controls Policy",
    "Establish an Information Classification, Labelling, and Handling Policy",
    "Establish a Mobile Devices Policy",
    "Establish an Operational Controls Policy",
    "Establish a Physical and Environmental Security Policy",
    "Establish a Protection from Malware Policy",
    "Establish a Protection of Personal Information Policy",
    "Establish a Remote Working Policy",
    "Establish a Supplier Policy",
    "Establish a Threat Intelligence Policy",
    "Establish a Use of Intellectual Property Policy",
    "Establish a Use of Software Policy",
    "Establish an information security incident response process",
    "Establish an information security change management process",
]
AUDITOR_TASKS = [
    "Create a Statement of Applicability",
]

OUTPUT_MAPPINGS = [
    (OUTPUTS_DIR / "asset_register.md", ASSET_TASKS),
    (OUTPUTS_DIR / "risk_register.md", RISK_TASKS),
    (OUTPUTS_DIR / "risk_treatment_plan.md", TREATMENT_TASKS),
    (OUTPUTS_DIR / "policies" / "security_policies.md", POLICY_TASKS),
    (OUTPUTS_DIR / "statement_of_applicability.md", AUDITOR_TASKS),
]


def _ensure_file() -> None:
    if not STATUS_FILE.exists():
        statuses = {task: "Incomplete" for task in TASK_ORDER}
        STATUS_FILE.write_text(json.dumps(statuses, indent=2), encoding="utf-8")


def load_statuses() -> Dict[str, str]:
    _ensure_file()
    return json.loads(STATUS_FILE.read_text(encoding="utf-8"))


def save_statuses(statuses: Dict[str, str]) -> None:
    STATUS_FILE.write_text(json.dumps(statuses, indent=2), encoding="utf-8")


def mark_tasks(tasks: Iterable[str], status: str = "Complete") -> None:
    statuses = load_statuses()
    updated = False
    for task in tasks:
        if statuses.get(task) != status:
            statuses[task] = status
            updated = True
    if updated:
        save_statuses(statuses)


def build_readiness_table() -> str:
    statuses = load_statuses()
    rows: List[str] = ["| Task | Status |", "| --- | --- |"]
    for task in TASK_ORDER:
        rows.append(f"| {task} | {statuses.get(task, 'Incomplete')} |")
    return "\n".join(rows)


def update_status_from_outputs() -> None:
    for path, tasks in OUTPUT_MAPPINGS:
        if path.exists():
            mark_tasks(tasks)
