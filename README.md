# ISO27001 AI Compliance Pipeline

This project runs a multi-agent ISO 27001 readiness assessment using [CrewAI](https://crewai.com). It reads your organization’s context, consults an ISO knowledge base (RAG), and automatically produces the documents auditors expect: asset register, risk register, treatment plan, policies, Statement of Applicability, and an executive-ready report.

---
## 1. Environment Variables (Required for Any Setup)
Create a `.env` file before running locally or via Docker (copy `.env.example` to get started):
```
HUGGINGFACE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2       # embedding model (default; downloads locally without API keys)
OPENAI_API_KEY=sk-...                         # optional, only if using OpenAI-compatible tools
OPENAI_BASE_URL=https://...                   # optional custom LLM endpoint
OPENAI_MODEL_NAME=glm-4.5-flash               # optional custom LLM model
```
Add any other provider tokens your tools need. The pipeline reads `.env` automatically when running locally (via your shell) or you can pass it to Docker with `--env-file .env`.

---
## 2. Local Setup (Without Docker)
| Requirement | Notes |
| --- | --- |
| Python 3.10–3.13 | Required for local execution. |
| [uv](https://docs.astral.sh/uv/) | Install with `pip install uv`. |
| Disk space (~3 GB) | Needed for the `BAAI/bge-m3` embedding model. |

### Steps
1. **Clone & install**
   ```bash
   git clone <repo-url>
   cd iso27001
   uv sync
   ```
   On macOS Intel, if you need a fresh environment:
   ```bash
   rm -rf .venv uv.lock
   uv venv --python 3.11
   source .venv/bin/activate
   uv sync
   ```
2. **Edit shared memory** (`memory/system_context.json`) with your latest asset/risk/policy data.
3. **Update knowledge base** by editing files in `knowledge_base/` as needed.
4. **Rebuild RAG embeddings** whenever step 3 changes:
   ```bash
   uv run python -m iso27001.knowledge.rag_loader
   ```
5. **Run the crew**
   ```bash
   uv run crewai run
   ```
6. **Review outputs** in `outputs/`.

Optional commands:
```bash
uv run crewai train 3 logs/session.json   # improve agents
uv run crewai replay <task_id>            # replay specific task
uv run crewai test 2 gpt-4o-mini          # run evaluations
```

---
## 3. Docker Setup (Portable Option)
Docker bundles Python, uv, and dependencies. After creating `.env`:

1. **Build image**
   ```bash
   docker build -t iso27001-crew .
   ```
2. **Rebuild embeddings (when knowledge base changes)**
   ```bash
   docker run --rm \
     -v $(pwd)/vector_db:/app/vector_db \
     --env-file .env \
     iso27001-crew uv run python -m iso27001.knowledge.rag_loader
   ```
3. **Run the full crew**
   ```bash
   docker run --rm \
     -v $(pwd)/outputs:/app/outputs \
     -v $(pwd)/vector_db:/app/vector_db \
     --env-file .env \
     iso27001-crew
   ```
   Append another command if desired (e.g., `... iso27001-crew uv run crewai train`).

Mounting `outputs/` and `vector_db/` ensures artifacts and embeddings persist on the host.

### Docker Compose
To run both the crew and the control API/UI, use the provided `docker-compose.yml`:
```bash
docker compose up --build
```
This starts two services:
- `iso27001-crew`: runs `uv run crewai run`
- `iso27001-control-api`: exposes the FastAPI bridge on port 5050 (use with `guide/control_center.html`)
All necessary directories (`outputs/`, `vector_db/`, `knowledge_base/`, `memory/`, `policies/`) are mounted so you can edit them on the host.

---
## 4. Web Control Center (Optional UI)
Launch the dashboard to manage inputs, RAG, and agent runs without touching the CLI:
```bash
uv run uvicorn guide.control_api:app --reload --port 5050
```
Open `guide/control_center.html` in a browser (double-click or serve via `python -m http.server`). It provides:
- Forms to save `.env` variables
- Text area to edit `memory/system_context.json`
- Markdown upload form for `knowledge_base/`
- Buttons to rebuild RAG, run the crew, and stop a run in progress
- Live log console, progress cards, and outputs list
- One-click "Load Demo Inputs" button that populates sample system context and knowledge files if you just want to test the pipeline

Keep the FastAPI process running while the dashboard is in use.

---
## 5. Inputs the Crew Needs
1. **Readiness Checklist** – already embedded in `src/iso27001/main.py` (`READINESS_TABLE`). Update as needed.
2. **Shared Context Memory** – edit `memory/system_context.json` to describe current assets, risks, policies, and treatment plans.
3. **Knowledge Base (RAG)** – Markdown files in `knowledge_base/`. The project ships with:
   - `iso27001_clauses.md`
   - `iso27001_annexA_controls.md`
   - `iso27002_guidance.md`
   - `risk_management_guidelines.md`
   Replace the demo content by copying your real clause/control guidance into those `.md` files or adding new ones. Remove unwanted demo files and rebuild the RAG (next section).
4. **Environment Variables** – already covered in Section 1; ensure `.env` is kept current.

---
## 6. Build the Knowledge Base (RAG)
Whenever you edit files in `knowledge_base/`, rebuild embeddings (default model is `sentence-transformers/all-MiniLM-L6-v2`; change `HUGGINGFACE_EMBEDDING_MODEL` if you prefer another model, and keep it consistent between RAG builds and runtime):
```bash
export HUGGINGFACE_EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
uv run python -m iso27001.knowledge.rag_loader
```
Common sources:
- Copy/paste text from PDFs into a new `.md`
- Summaries of internal policies or vendor questionnaires
- Mapping tables between ISO and other frameworks
- Threat/risk catalogs or treatment checklists

Replacing demo data:
- Delete or overwrite the default demo `.md` files in `knowledge_base/` with your real content.
- Update `memory/system_context.json` to reflect real assets, risks, policies, and treatment plans (you can use the web control center’s “Load Demo Inputs” button for a starting template, then edit the JSON).
- After making changes, rerun the RAG loader command above so the vector DB reflects your latest documents.

The loader chunks each Markdown file, generates embeddings, and stores them in `vector_db/iso27001_knowledge`. Agents query this via the `ISOKnowledgeRetriever` tool.

---
## 7. Quickstart Run
```bash
# 1) Install deps (already done if you ran uv sync)
uv sync

# 2) Edit memory/system_context.json with live data
# 3) Rebuild RAG (if knowledge base changed)
uv run python -m iso27001.knowledge.rag_loader

# 4) Run the crew
uv run crewai run

# 5) Review outputs
ls outputs/
```
All crew commands accept the same inputs; other useful options:
```bash
uv run crewai train 3 logs/session.json   # iterate/learn
uv run crewai test 2 gpt-4o-mini          # run evaluation
uv run crewai replay <task_id>            # replay a specific task
```

---
## 8. Agent Workflow (What Happens When You Run It)
1. **ISO Consultant Agent** – analyzes context/scope/stakeholders.
2. **Asset Inventory Agent** – writes `outputs/asset_register.md`.
3. **Risk Assessment Agent** – uses RAG + memory to produce `outputs/risk_register.md`.
4. **Risk Treatment Agent** – maps risks to controls → `outputs/risk_treatment_plan.md`.
5. **Policy Writer Agent** – drafts policies → `outputs/policies/security_policies.md`.
6. **Compliance Auditor Agent** – creates `outputs/statement_of_applicability.md`.
7. **Documentation Agent** – compiles everything into `outputs/iso27001_readiness_report.md`.

Each agent pulls from:
- **Shared memory** (`system_context`) for existing assets, risks, policies.
- **RAG knowledge base** for ISO clauses, Annex A controls, ISO27002 guidance.
- **Prior outputs** (stored in `outputs/`) when referencing previous stages.

---
## 9. Output Directory Structure
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
These Markdown files are ready for auditors, leadership reviews, or downstream tooling.

---
## 10. Customizing & Extending
- **Agents/Tasks**: edit `src/iso27001/config/agents.yaml` and `src/iso27001/config/tasks.yaml`.
- **Tools**: add modules under `src/iso27001/tools/` and attach them via `crew.py`.
- **Memory**: augment `memory/system_context.json` with additional sections (e.g., vendor lists, audit history).
- **Knowledge Base**: add more Markdown files (site-specific procedures, regulatory mappings) and rerun the RAG loader.

## 11. Troubleshooting
| Issue | Fix |
| --- | --- |
| Embedding build fails | Ensure `sentence-transformers` downloaded the model (rerun with `HF_HUB_ENABLE_HF_TRANSFER=1`). |
| Outputs missing/outdated | Delete files under `outputs/` and rerun `uv run crewai run`. |
| Vector DB corrupted | Delete `vector_db/` and rebuild via `rag_loader`. |
| Docker build slow | Pre-download models locally or mount `.cache/huggingface`. |
| Need deterministic runs | Set `CREWAI_LOG_LEVEL=INFO` and pin LLM settings in `.env`. |

You now have a fully documented pipeline to generate ISO 27001 readiness artifacts with RAG-grounded AI agents.
