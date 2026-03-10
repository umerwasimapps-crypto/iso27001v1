# Repository Guidelines

## Project Structure & Module Organization
- `src/iso27001/` contains the CrewAI package: `crew.py` wires agents/tasks, `main.py` defines CLI entrypoints, and `tools/` holds helpers like `ISOKnowledgeRetriever` and RAG utilities.
- Configuration lives in `src/iso27001/config/` (`agents.yaml`, `tasks.yaml`). Update these when changing prompts, outputs, or tool attachments.
- Shared context memory resides in `memory/system_context.json`; update it whenever asset/risk/policy data changes.
- RAG sources go in `knowledge_base/*.md`; run `uv run python -m iso27001.knowledge.rag_loader` after editing to refresh `vector_db/`.
- Web assets (HTML/CSS/JS + FastAPI bridge) live under `guide/` for the non-technical control center.
- Generated artifacts land in `outputs/` (asset register, risk register, treatment plan, policies, SoA, readiness report).

## Build, Test, and Development Commands
- Install deps: `uv sync` (or Mac Intel reset: `rm -rf .venv uv.lock && uv venv --python 3.11 && source .venv/bin/activate && uv sync`).
- Local workflow: `uv run crewai run`. Training/replay/test: `uv run crewai train 3 logs/session.json`, `uv run crewai replay <task_id>`, `uv run crewai test 2 gpt-4o-mini`.
- Docker workflow: `docker build -t iso27001-crew .`, optional `docker run ... uv run python -m iso27001.knowledge.rag_loader`, main run `docker run ... iso27001-crew`.
- Web control: `uv run uvicorn guide.control_api:app --reload --port 5050`, then open `guide/control_center.html` for a point-and-click experience (env vars, system context, knowledge uploads, run/stop buttons, progress view).

## Coding Style & Naming Conventions
- Python: PEP 8, type hints, small functions, avoid duplicate logic by isolating utilities (`vector_store.py`, `rag_loader.py`).
- YAML: 2-space indentation, keep placeholders (`{organization_name}`, `{analysis_focus}`), no trailing spaces.
- JS/CSS (control center): keep functions modular, prefer Fetch API, avoid inline scripts for maintainability.
- Treat knowledge_base Markdown files as structured data—use headings, tables, or bullet lists so embeddings remain meaningful.

## Testing & Validation
- Prefer `uv run crewai test ...` for end-to-end regression. Seed stable inputs in `system_context.json` so comparisons are meaningful.
- For new tools or APIs, add unit tests under `tests/` (e.g., mock Chroma interactions) to ensure deterministic behavior.
- When editing the control API/UI, manually verify POST endpoints (`/api/save-env`, `/api/run/rag`, `/api/stop`) using the browser console or curl.

## RAG & Memory Hygiene
- Every time you edit `knowledge_base/`, rerun the RAG loader (local or Docker). Empty vectors mean agents rely solely on prompts.
- Keep `memory/system_context.json` valid JSON (no raw newlines in strings). Use `\n` if you need multi-line summaries.
- If `vector_db/` corrupts, delete it and rebuild via the loader.

## Commit & PR Guidelines
- Use Conventional Commits (`feat: add web control center`, `fix: remove stale tool config`).
- Include screenshots/GIFs when changing the UI or output files. Highlight new commands in PR descriptions.
- Avoid committing secrets; `.env` should stay in `.gitignore`.

## Security & Ops Tips
- Store API keys and model endpoints in `.env`; never hardcode in source.
- Review knowledge uploads for PII before running the crew. Use the web UI’s Markdown form for quick edits.
- When running in Docker, mount `outputs/` and `vector_db/` so artifacts persist. Stop runs via the web UI “Stop” button or Ctrl+C in the CLI.

Following these guidelines keeps the multi-agent pipeline consistent, reproducible, and friendly for both developers and compliance stakeholders.
