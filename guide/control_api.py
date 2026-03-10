"""Simple REST API to bridge the ISO27001 CLI with a web UI."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List

import os
import signal
import threading
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEMORY_FILE = PROJECT_ROOT / "memory" / "system_context.json"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge_base"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
ENV_FILE = PROJECT_ROOT / ".env"

app = FastAPI(title="ISO27001 Control API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"]
)


current_process: subprocess.Popen | None = None
process_log: List[str] = []
log_lock = threading.Lock()


def _append_log(message: str) -> None:
    with log_lock:
        process_log.append(message)


def _stream_output(proc: subprocess.Popen) -> None:
    assert proc.stdout is not None
    for line in proc.stdout:
        _append_log(line.rstrip())
    proc.wait()
    _append_log(f"Process exited with code {proc.returncode}")


def _start_process(command: List[str]) -> Dict[str, str]:
    global current_process
    if current_process and current_process.poll() is None:
        raise HTTPException(status_code=409, detail="Another process is running")

    process_log.clear()
    _append_log(f"$ {' '.join(command)}")

    current_process = subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    threading.Thread(target=_stream_output, args=(current_process,), daemon=True).start()
    return {"status": "started"}


@app.post("/api/save-env")
def save_env(data: Dict[str, str]):
    lines = [f"{key}={value}" for key, value in data.items() if value is not None]
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"status": "saved", "path": str(ENV_FILE)}


@app.post("/api/save-system-context")
def save_system_context(payload: Dict):
    MEMORY_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"status": "saved", "path": str(MEMORY_FILE)}


@app.post("/api/add-knowledge")
def add_knowledge(doc: Dict[str, str]):
    filename = doc.get("filename", "user_note.md")
    if not filename.endswith(".md"):
        filename += ".md"
    content = doc.get("content", "")
    if not content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    path = KNOWLEDGE_DIR / filename
    path.write_text(content, encoding="utf-8")
    return {"status": "saved", "path": str(path)}


@app.post("/api/run/rag")
def run_rag():
    return _start_process(["uv", "run", "python", "-m", "iso27001.knowledge.rag_loader"])


@app.post("/api/run/crew")
def run_crew():
    return _start_process(["uv", "run", "crewai", "run"])


@app.post("/api/demo/populate")
def populate_demo():
    MEMORY_FILE.write_text(json.dumps(DEMO_CONTEXT, indent=2), encoding="utf-8")
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in DEMO_KNOWLEDGE.items():
        (KNOWLEDGE_DIR / name).write_text(content, encoding="utf-8")
    return {"status": "demo-data-created", "context": DEMO_CONTEXT}


@app.post("/api/stop")
def stop_process():
    global current_process
    if current_process and current_process.poll() is None:
        os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        current_process = None
        _append_log("Process terminated by user")
        return {"status": "stopped"}
    raise HTTPException(status_code=400, detail="No running process")


@app.get("/api/logs")
def get_logs():
    running = current_process is not None and current_process.poll() is None
    with log_lock:
        logs = list(process_log)
    return {"running": running, "logs": logs}


@app.get("/api/progress")
def get_progress():
    outputs = {
        "asset_register": (OUTPUTS_DIR / "asset_register.md").exists(),
        "risk_register": (OUTPUTS_DIR / "risk_register.md").exists(),
        "risk_treatment_plan": (OUTPUTS_DIR / "risk_treatment_plan.md").exists(),
        "policies": (OUTPUTS_DIR / "policies" / "security_policies.md").exists(),
        "statement_of_applicability": (OUTPUTS_DIR / "statement_of_applicability.md").exists(),
        "final_report": (OUTPUTS_DIR / "iso27001_readiness_report.md").exists(),
    }
    return outputs


@app.get("/api/outputs")
def list_outputs():
    if not OUTPUTS_DIR.exists():
        return []
    files = []
    for path in sorted(OUTPUTS_DIR.rglob("*.md")):
        rel = path.relative_to(OUTPUTS_DIR)
        files.append({"name": str(rel), "size": path.stat().st_size})
    return files


@app.get("/api/readiness")
def get_readiness():
    from iso27001.status_tracker import load_statuses

    statuses = load_statuses()
    return statuses
DEMO_CONTEXT = {
    "asset_register": {
        "summary": "Demo asset inventory covering data warehouse and laptops.",
        "entries": [
            {
                "asset_name": "Customer Data Warehouse",
                "asset_type": "Structured data platform",
                "owner": "Data Engineering",
                "classification": "Confidential",
                "business_importance": "High"
            },
            {
                "asset_name": "Employee Laptops",
                "asset_type": "Endpoint devices",
                "owner": "IT Operations",
                "classification": "Internal",
                "business_importance": "High"
            }
        ]
    },
    "risk_register": {
        "summary": "Demo risks: unauthorized DB access and lost backup media.",
        "entries": [
            {
                "risk": "Unauthorized database access",
                "likelihood": "Medium",
                "impact": "High",
                "existing_controls": ["MFA", "Network segmentation"],
                "relevant_controls": ["A.8.2"]
            },
            {
                "risk": "Loss of backup media",
                "likelihood": "Low",
                "impact": "High",
                "existing_controls": ["Encrypted backup storage"],
                "relevant_controls": ["A.8.12"]
            }
        ]
    },
    "policies": {
        "summary": "Demo Access Control, Backup, Mobile Device, and Incident Response policies.",
        "links": {
            "Access Control Policy": "policies/access_control.md",
            "Backup Policy": "policies/backup_policy.md",
            "Mobile Device Policy": "policies/mobile_device_policy.md",
            "Incident Response Policy": "policies/incident_response.md"
        }
    },
    "risk_treatment_plan": {
        "summary": "Demo treatment plan for PAM and backup hardening.",
        "workstreams": [
            {
                "name": "Privileged Access Management",
                "owner": "Security Operations",
                "target_date": "2024-08",
                "controls": ["A.8.2"]
            },
            {
                "name": "Backup Hardening",
                "owner": "Infrastructure",
                "target_date": "2024-07",
                "controls": ["A.8.12"]
            }
        ]
    }
}

DEMO_KNOWLEDGE = {
    "demo_clauses.md": "# Demo ISO27001 Clauses\n## Clause 5 Leadership\nManagement establishes policy and assigns roles.",
    "demo_annexA.md": "# Demo Annex A Controls\n| Control_ID | Description |\n| --- | --- |\n| A.8.2 | Privileged access must be monitored. |",
}
