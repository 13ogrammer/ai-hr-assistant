# HR Assistant - API

A naive end-to-end RAG pipeline answering HR policy questions for a fictional company (`docs/`): chunk the policy documents, embed them locally, store them in Postgres/pgvector, retrieve the most relevant chunks for a question, and ask an LLM to answer from them.

No access control, no citation verification, no relevance threshold yet - deliberately naive as a first build-plan chapter, not an oversight.

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

## Run

```bash
uv run uvicorn main:app --reload --port 8000
```

- `GET /health` - liveness check.
- `POST /ask` - `{"question": "..."}` in, `{"answer": "...", "sources": ["..."]}` out.

CORS is configured to allow requests from `http://localhost:5173` (the `apps/web` dev server) only.

## Test

```bash
uv run pytest
```

Pure unit tests (chunking logic) run with no dependencies. Integration tests against retrieval require Postgres running and docs already ingested (steps 1 and 4 above). Generation and API-layer tests mock the OpenAI client and the retrieval/generation functions respectively, so they run without a real API key or network access.
