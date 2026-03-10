#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from iso27001.crew import Iso27001
from iso27001.memory import load_system_context
from iso27001.status_tracker import (
    build_readiness_table,
    mark_tasks,
    update_status_from_outputs,
    CONSULTANT_TASKS,
)

READINESS_TABLE = """
| Task | Status |
| --- | --- |
| Determine Internal and External Issues | Incomplete |
| Determine Interested Parties | Incomplete |
| Determine certification scope | Incomplete |
| Establish organisational processes | Incomplete |
| Establish an Information Security Policy | Incomplete |
| Establish roles and responsibilities | Incomplete |
| Determine business risks and opportunities | Incomplete |
| Determine information security legal obligations | Incomplete |
| Establish Information Security Objectives | Incomplete |
| Establish infrastructure and asset maintenance schedules | Incomplete |
| Establish employee competence and skills management | Incomplete |
| Establish and manage communications | Incomplete |
| Establish control of documentation | Incomplete |
| Establish supplier management processes | Incomplete |
| Establish an internal audit plan | Incomplete |
| Capturing internal audit results | Incomplete |
| Define and capture management review meeting minutes | Incomplete |
| Establish how non conformities, risks, and opportunities are captured | Incomplete |
| Establish an Acceptable Use of Assets Policy | Incomplete |
| Establish an Access Control Policy | Incomplete |
| Establish a Backup Policy | Incomplete |
| Establish a Clear Desk and Clear Screen Policy | Incomplete |
| Establish a Configuration Management Policy | Incomplete |
| Establish a Cryptographic Controls Policy | Incomplete |
| Establish an Information Classification, Labelling, and Handling Policy | Incomplete |
| Establish a Mobile Devices Policy | Incomplete |
| Establish an Operational Controls Policy | Incomplete |
| Establish a Physical and Environmental Security Policy | Incomplete |
| Establish a Protection from Malware Policy | Incomplete |
| Establish a Protection of Personal Information Policy | Incomplete |
| Establish a Remote Working Policy | Incomplete |
| Establish a Supplier Policy | Incomplete |
| Establish a Threat Intelligence Policy | Incomplete |
| Establish a Use of Intellectual Property Policy | Incomplete |
| Establish a Use of Software Policy | Incomplete |
| Establish an information security incident response process | Incomplete |
| Establish an information security change management process | Incomplete |
| Determine credible business continuity disruption events and analyse their impact | Incomplete |
| Establish screening checks | Incomplete |
| Establish appropriate terms and conditions of employment | Incomplete |
| Establish a formal disciplinary process | Incomplete |
| Establish confidentiality or non-disclosure agreements | Incomplete |
| Establish an Information Asset Register | Incomplete |
| Establish an information security risk assessment criteria | Incomplete |
| Determine and assess information security risks | Incomplete |
| Establish and maintain risk treatment plans | Incomplete |
| Create a Statement of Applicability | Incomplete |
"""


def _build_inputs() -> dict:
    from iso27001.status_tracker import load_statuses

    update_status_from_outputs()

    readiness_table = build_readiness_table()
    if "|" not in readiness_table:
        readiness_table = READINESS_TABLE.strip()

    return {
        "organization_name": "ACME Corp",
        "analysis_focus": "ISO 27001 readiness assessment",
        "current_year": str(datetime.now().year),
        "readiness_table": readiness_table,
        "system_context": load_system_context(),
        "organization_description": (
            "ACME Corp is a mid-size SaaS company providing customer analytics platforms. "
            "It handles large volumes of structured customer data and supports a remote workforce."
        ),
        "business_processes": (
            "Customer data ingestion and reporting, software engineering for the SaaS platform, "
            "customer success/support operations, vendor management, IT operations, and security operations."
        ),
        "infrastructure_notes": (
            "Centralized customer data warehouse hosted in secure cloud infrastructure, company-issued encrypted "
            "laptops managed through MDM, VPN/zero-trust remote access, and encrypted backup systems with "
            "quarterly recovery tests."
        ),
    }

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = _build_inputs()

    try:
        Iso27001().crew().kickoff(inputs=inputs)
        mark_tasks(CONSULTANT_TASKS)
        update_status_from_outputs()
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = _build_inputs()
    try:
        Iso27001().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Iso27001().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = _build_inputs()

    try:
        Iso27001().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = _build_inputs()
    inputs["crewai_trigger_payload"] = trigger_payload

    override_keys = {"organization_name", "analysis_focus", "current_year", "readiness_table"}
    for key in override_keys:
        if key in trigger_payload:
            inputs[key] = trigger_payload[key]

    try:
        result = Iso27001().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
