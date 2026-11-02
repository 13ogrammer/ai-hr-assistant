# HR Assistant - API

An end-to-end RAG pipeline answering HR policy questions for a fictional company (`docs/`): chunk the policy documents, embed them locally, store them in Postgres/pgvector, retrieve the most relevant chunks for a question - filtered by the asker's role - and ask an LLM to answer from them.

**Access control (Chapter 2):** every chunk is tagged at ingestion with an `access_level` (`public`/`internal`/`confidential`/`restricted`) and the roles it maps to (`shared/access.py`). `retrieve()` applies this as a SQL `WHERE role = ANY(allowed_roles)` filter, so a restricted chunk is never fetched for a role that can't see it - it never reaches the model, regardless of how the question is phrased. There's no real login yet: `shared/users.py` is a small fake user directory, and the caller sends a `user_id` that the API resolves to a role server-side (never a role sent directly by the client).

**Structured data behind tools (Chapter 3):** salary and leave balance are per-employee facts, not policy text - putting them in the vector store only gets you a vague band or a stale figure, and it's a liability besides. `shared/employees.py` queries a Postgres `employees` table (seeded by `scripts/seed_employees.py` - a one-off fixture load standing in for an HRIS's own writes, kept separate from the `ingestion/` document pipeline) for these instead. `generate_answer()` gives the model `get_salary`/`get_leave_balance` as tools (`tools/hr_tools.py`); the model proposes an `employee_id` argument from the question text, but that argument is never trusted - `resolve_employee_id()` overwrites it from the caller's real session identity before any lookup runs. A non-HR caller is hard-locked to their own record no matter what they (or a prompt injection) ask for; HR can target any id, and every lookup is logged. See `tests/test_tools.py` for the adversarial cases this defends against.

No citation verification, no relevance threshold, and no router between tools and document search yet (the model's own tool-calling decides) - deliberately naive beyond chapter 3's scope, not an oversight.

## Setup

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/), and Docker.

1. Start Postgres (with the pgvector extension):
   ```bash
   docker compose up -d
   ```
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Create `.env` with:
   ```
   DATABASE_URL=postgresql://hr_assistant:hr_assistant@localhost:5432/hr_assistant
   OPENAI_API_KEY=<your key>
   ```
4. Ingest the HR documents (chunks them, embeds them with `fastembed`, stores them in Postgres):
   ```bash
   uv run python -m ingestion.ingest
   ```
   If you're upgrading from before Chapter 2, the `chunks` table needs the new `access_level`/`allowed_roles` columns - drop it first (`DROP TABLE chunks;` via `psql` or `docker compose exec db psql -U hr_assistant -d hr_assistant`) and re-run ingestion; it's fully reproducible from `docs/`.
5. Seed the fake employee records (`shared/employees.py`'s system of record for `get_salary`/`get_leave_balance`) - a one-off fixture load standing in for an HRIS's own writes, not part of the document-ingestion pipeline, so it lives in `scripts/` rather than `ingestion/`:
   ```bash
   uv run python -m scripts.seed_employees
   ```

## Run

```bash
uv run uvicorn main:app --reload --port 8000
```

- `GET /health` - liveness check.
- `GET /users` - the fake user directory (`id`, `name`, `title`, `role`) for the UI's "asking as" selector.
- `POST /ask` - `{"question": "...", "user_id": "..."}` in, `{"answer": "...", "sources": ["..."]}` out. `user_id` must match one of `/users`.

CORS is configured to allow requests from `http://localhost:5173` (the `apps/web` dev server) only.

## Test

```bash
uv run pytest
```

Pure unit tests (chunking logic, tool identity-enforcement) run with no dependencies. Integration tests against retrieval and the employees table require Postgres running and docs/employees already ingested/seeded (steps 1, 4, and 5 above). Generation and API-layer tests mock the OpenAI client and the retrieval/generation functions respectively, so they run without a real API key or network access.
