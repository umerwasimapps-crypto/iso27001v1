# ISO27001 AI Compliance Pipeline

This project runs a multi-agent ISO 27001 readiness assessment using [CrewAI](https://crewai.com). It ingests your organization’s context, consults a Retrieval Augmented Generation (RAG) knowledge base, and produces the artifacts auditors expect (asset register, risk register, treatment plan, policies, Statement of Applicability, executive-ready report, etc.).

---
## 1. Environment Variables (Required for Any Setup)
Create `.env` (copy `.env.example` to get started):
```
HUGGINGFACE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2       # embedding model (default; downloads locally without API keys)
OPENAI_API_KEY=sk-...                         # optional, only if using OpenAI-compatible tools
OPENAI_BASE_URL=https://...                   # optional custom LLM endpoint
OPENAI_MODEL_NAME=glm-4.5-flash               # optional custom LLM model
```
Keep this file current before running locally or via Docker.

---
## 2. Local Setup (Without Docker)
| Requirement | Notes |
| --- | --- |
| Python 3.10–3.13 | Required for local execution |
| [uv](https://docs.astral.sh/uv/) | Install via `pip install uv` |
| Disk space (~3 GB) | Required to download the embedding model |

### Steps
1. **Clone & install**
   ```bash
   git clone <repo-url>
   cd iso27001
   uv sync
   ```
   *(macOS Intel clean env: `rm -rf .venv uv.lock && uv venv --python 3.11 && source .venv/bin/activate && uv sync`)*
2. **Edit shared memory** `memory/system_context.json` with real assets/risks/policies.
3. **Update knowledge base** by editing `knowledge_base/*.md`.
4. **Rebuild RAG**: `uv run python -m iso27001.knowledge.rag_loader` (see Section 6.
5. **Run the crew**: `uv run crewai run`
6. **Review outputs** in `outputs/`

Useful commands: `uv run crewai train ...`, `uv run crewai test ...`, `uv run crewai replay ...`

---
## 3. Docker Setup
1. `docker build -t iso27001-crew .`
2. Rebuild RAG: `docker run --rm -v $(pwd)/vector_db:/app/vector_db --env-file .env iso27001-crew uv run python -m iso27001.knowledge.rag_loader`
3. Run crew: `docker run --rm -v $(pwd)/outputs:/app/outputs -v $(pwd)/vector_db:/app/vector_db --env-file .env iso27001-crew`
4. **Docker Compose**: run both the crew and the control API
   ```bash
   docker compose up --build
   ```
   - `iso27001-crew`: executes `uv run crewai run`
   - `iso27001-control-api`: hosts FastAPI (port 5050) for the web control center

---
## 4. Web Control Center (Optional UI)
1. `uv run uvicorn guide.control_api:app --reload --port 5050`
2. Open `guide/control_center.html` (double-click or via `python -m http.server`).
3. Dashboard functions: save `.env`, edit `system_context.json`, upload Markdown knowledge, rebuild RAG, run/stop the crew, load demo inputs, view logs/progress, list outputs.

---
## 5. Inputs Required
1. **Readiness checklist** – `src/iso27001/main.py` includes `READINESS_TABLE`. Update as needed.
2. **Shared system context** – `memory/system_context.json`
3. **Knowledge base (RAG)** – Markdown files in `knowledge_base/`. Replace demo `.md` files with your real guidance and rerun RAG.
4. **Environment variables** – already covered in Section 1

---
## 6. Build the Knowledge Base (RAG)
```bash
export HUGGINGFACE_EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
uv run python -m iso27001.knowledge.rag_loader
```
Tips:
- Copy/paste text from PDFs/Word into `.md`
- Summaries of internal policies, audits, regulatory mappings
- Threat/risk catalogs, treatment checklists
- Delete or overwrite demo `.md` files and update `system_context`. Re-run the command whenever content changes.

---
## 7. Quickstart Run
```bash
uv sync
uv run python -m iso27001.knowledge.rag_loader
uv run crewai run
ls outputs/
```
Use `uv run crewai train|test|replay` for additional workflows.

---
## 8. Agent Workflow & Tools
1. **ISO Consultant Agent** (Senior consultant, 20+ years)
   - Tasks: organizational context, scope, stakeholders, management processes
   - Tools: `ISOKnowledgeRetriever`
   - Outputs: context/stakeholder/scope/process narratives
   - Readiness statuses: context/scope/leadership tasks
2. **Asset Inventory Agent** (Information Asset Management Specialist)
   - Tasks: asset register, supporting assets, owners, classifications
   - Tools: `ISOKnowledgeRetriever`
   - Outputs: `outputs/asset_register.md`
   - Readiness: asset register tasks
3. **Risk Assessment Agent** (ISO27005 analyst)
   - Tasks: risk criteria, threats, vulnerabilities, likelihood/impact
   - Tools: `ISOKnowledgeRetriever`
   - Outputs: `outputs/risk_register.md`
   - Readiness: risk assessment criteria, risk identification
4. **Risk Treatment Agent** (Risk Mitigation Specialist)
   - Tasks: prioritize risks, decide treatment, map to controls
   - Tools: `ISOKnowledgeRetriever`
   - Outputs: `outputs/risk_treatment_plan.md`
   - Readiness: treatment plans
5. **Policy Writer Agent** (ISO27002 policy specialist)
   - Tasks: draft policies, align with risks/treatments, document compliance
   - Tools: `ISOKnowledgeRetriever`
   - Outputs: `outputs/policies/security_policies.md`
   - Readiness: all policy rows
6. **Compliance Auditor Agent** (ISO27001 internal/lead auditor)
   - Tasks: evaluate controls, determine Annex A applicability, generate SoA
   - Tools: `ISOKnowledgeRetriever`
   - Outputs: `outputs/statement_of_applicability.md`
   - Readiness: Statement of Applicability and control verification
7. **Documentation Agent** (Compliance Documentation Specialist)
   - Tasks: gather artifacts, ensure completeness, compile final report, update readiness statuses
   - Tools: `ISOKnowledgeRetriever`, direct file access
   - Outputs: `outputs/iso27001_readiness_report.md`

Each agent consumes: shared `system_context`, RAG knowledge, and prior outputs.

---
## 9. Task Sequence (Detailed)
1. ISO Consultant Agent
   - `determine_context_task`
   - `identify_interested_parties_task`
   - `define_scope_task`
   - `establish_processes_task`
2. Asset Inventory Agent
   - `identify_information_assets_task`
   - `identify_supporting_assets_task`
   - `assign_asset_owners_task`
   - `classify_assets_task`
3. Risk Assessment Agent
   - `define_risk_assessment_criteria_task`
   - `identify_threats_task`
   - `identify_vulnerabilities_task`
   - `calculate_likelihood_impact_task`
   - `generate_risk_register_task`
4. Risk Treatment Agent
   - `evaluate_risks_task`
   - `decide_treatment_strategy_task`
   - `map_risks_to_controls_task`
   - `generate_risk_treatment_plan_task`
5. Policy Writer Agent
   - `generate_policies_task`
   - `align_policies_with_risk_treatment_task`
   - `ensure_policy_compliance_task`
6. Compliance Auditor Agent
   - `evaluate_controls_task`
   - `determine_control_applicability_task`
   - `generate_statement_of_applicability_task`
   - `identify_missing_controls_task`
7. Documentation Agent
   - `collect_agent_outputs_task`
   - `generate_final_documentation_task`
   - `ensure_audit_ready_task`
   - `readiness_review_task`

Statuses update automatically via `memory/readiness_status.json`. Each agent marks tasks complete once their outputs exist.

---
## 10. Output Directory Structure
```
outputs/
├── asset_register.md
├── risk_register.md
├── risk_treatment_plan.md
├── statement_of_applicability.md
├── policies/
│   └── security_policies.md
└── iso27001_readiness_report.md
```

---
## 11. Customization & Extending
- Edit `src/iso27001/config/agents.yaml` and `tasks.yaml`
- Add tools under `src/iso27001/tools/`
- Enhance `memory/system_context.json`
- Add more `.md` files in `knowledge_base/`

---
## 12. Troubleshooting
| Issue | Fix |
| --- | --- |
| RAG dimension mismatch | Delete `vector_db/`, rerun `uv run python -m iso27001.knowledge.rag_loader` with the same `HUGGINGFACE_EMBEDDING_MODEL`. |
| Embedding download fails | Set `HF_HUB_ENABLE_HF_TRANSFER=1` or retry; ensure internet access. |
| Outputs missing | Remove old files in `outputs/` and rerun the crew. |
| Vector DB corrupted | Delete `vector_db/`, rebuild via RAG loader. |
| Docker push fails (403) | Update GitHub credentials or PAT. |
| OpenAI timeout | Check network, API keys, or switch to a different LLM provider. |

You're ready to run the ISO 27001 readiness pipeline with RAG-grounded agents and a complete web/CLI workflow.
