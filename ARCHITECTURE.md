# ISO27001 Crew Architecture & Concepts

This document gives a conceptual tour of the project so readers understand each building block before diving into the full README.

---
## 1. Core Components

| Component | Purpose |
| --- | --- |
| **CrewAI** (`src/iso27001/crew.py`) | Orchestrates agents and tasks sequentially. Each agent has a role/backstory, and tasks define the work units. |
| **Inputs Loader** (`src/iso27001/main.py`) | Prepares inputs for the crew: readiness table, system context, organization description, etc. |
| **Shared Memory** (`memory/system_context.json`) | Stores assets, risks, policies, and treatment plans. Agents read/update this context. |
| **Readiness Status Tracker** (`memory/readiness_status.json`, `src/iso27001/status_tracker.py`) | Tracks the status of each readiness checklist item; updated as agents produce outputs. |
| **RAG Knowledge Base** (`knowledge_base/` + `vector_db/`) | Markdown sources embedded with `sentence-transformers/all-MiniLM-L6-v2`, served via ChromaDB for retrieval. |
| **Tools** (`src/iso27001/tools/`) | Reusable utilities, especially `ISOKnowledgeRetriever` for RAG queries. |
| **Outputs** (`outputs/`) | Generated artifacts (asset register, risk register, treatment plan, policies, Statement of Applicability, readiness report). |

---
## 2. Agent & Task Flow (Conceptual)

```
Organization Context → ISO Consultant → Asset Inventory → Risk Assessment → Risk Treatment → Policy Writer → Compliance Auditor → Documentation Agent
```

Each agent reads the inputs, calls `ISOKnowledgeRetriever` for ISO references, writes outputs, and updates readiness statuses. The entire pipeline runs sequentially so every stage has the previous stage’s context.

---
## 3. Key Concepts

### Readiness Table & Status Tracker
- The readiness checklist is defined in `src/iso27001/main.py` and mirrored in `memory/readiness_status.json`.
- `status_tracker.py` loads/saves statuses and rebuilds the table dynamically. As outputs appear (`outputs/asset_register.md`, etc.), statuses flip to “Complete”.

### System Context Memory
- `memory/system_context.json` provides seed data (assets, risks, policies, treatment plan).
- Agents reference this to avoid re-asking for inputs. Update it with your real data before running the crew.

### RAG Vector Store
- Markdown files in `knowledge_base/` are chunked and embedded via `sentence-transformers/all-MiniLM-L6-v2`.
- Command: `uv run python -m iso27001.knowledge.rag_loader` (preload caches with `UV_CACHE_DIR=$(pwd)/.uv_cache`).
- Chroma stores embeddings under `vector_db/` (collection directories named by UUID). If you switch models, delete `vector_db/` and rebuild.

### Tools & Retrieval
- `ISOKnowledgeRetriever` queries the Chroma collection with agent questions (`collection.query(query_texts=[question], n_results=3)`).
- Agents include the tool in `crew.py`, so they can cite Annex A or Clause guidance in their answers.

### Web Control Center
- FastAPI backend (`guide/control_api.py`) exposes endpoints for `.env` saves, system context edits, knowledge uploads, RAG/crew commands, logs, progress, readiness statuses.
- Frontend (`guide/control_center.html/css/js`) provides forms, buttons, progress cards, and a console for non-technical use.

---
## 4. Example End-to-End Scenario

1. **Prepare Inputs**
   - Edit `.env` (embedding model, optional LLM keys).
   - Update `memory/system_context.json` with real assets/risks/policies.
   - Add Markdown files to `knowledge_base/` (e.g., `policies/aligned_guidance.md`).

2. **Build RAG**
   ```bash
   UV_CACHE_DIR=$(pwd)/.uv_cache uv run python -m iso27001.knowledge.rag_loader
   ```

3. **Run Crew**
   ```bash
   uv run crewai run
   ```
   - ISO Consultant agent completes context/scope tasks and updates statuses.
   - Asset Inventory agent writes `outputs/asset_register.md` and updates readiness items.
   - Risk Assessment agent generates `outputs/risk_register.md` and marks risk tasks complete.
   - Risk Treatment, Policy Writer, Compliance Auditor, and Documentation Agents follow suit.

4. **Review Outputs**
   - Inspect `outputs/asset_register.md`, `outputs/risk_register.md`, `outputs/risk_treatment_plan.md`, `outputs/policies/security_policies.md`, `outputs/statement_of_applicability.md`, `outputs/iso27001_readiness_report.md`.
   - Readiness statuses in `memory/readiness_status.json` reflect completed tasks.

5. **Iterate**
   - If knowledge base or system context changes, rebuild RAG and rerun the crew.
   - Use the web UI for an interactive workflow (save `.env`, load demo data, run/stop the pipeline, monitor logs/progress).

---
## 5. Extending the Architecture

- **Add new agents**: define roles/tasks in `src/iso27001/config/agents.yaml` / `tasks.yaml`, wire them in `crew.py`.
- **Add tools**: implement in `src/iso27001/tools/`, then add to relevant agents.
- **Track new readiness metrics**: add entries to `memory/readiness_status.json` and update `status_tracker.py` to mark them complete when outputs exist.
- **Alternate embedding models**: change `HUGGINGFACE_EMBEDDING_MODEL`, delete `vector_db/`, rerun the RAG loader.

This architecture keeps data flow explicit (system context + RAG + outputs) and allows non-technical users to follow the pipeline via the README and web control center.
