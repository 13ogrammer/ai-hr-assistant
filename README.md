# HR Assistant

A RAG-based HR policy Q&A assistant for a fictional company, built chapter-by-chapter as a learning project. A monorepo with two independently deployable apps:

- **[apps/api](apps/api)** — the FastAPI backend: ingestion, retrieval, generation, and the `/ask` endpoint. See its own README for setup and running instructions.
- **[apps/web](apps/web)** — a Vite + React chat UI that calls the backend's `/ask` endpoint. See its own README for setup instructions.

Each app has its own dependency manager and lockfile (`uv`/`pyproject.toml` for the API, `npm`/`package.json` for the web app) and is meant to be run and deployed independently.

## Run both together

```bash
npm install   # once, installs concurrently for this root-level orchestration script
npm run dev
```

Starts the FastAPI backend on `:8000` and the Vite dev server on `:5173`, labeled and color-coded in one terminal. Requires `apps/api`'s own setup (Postgres via Docker, dependencies installed, `.env` configured, docs ingested) to already be done - see [apps/api/README.md](apps/api/README.md).

## Design

The web UI's visual system is documented in [DESIGN.md](DESIGN.md); product context (users, purpose, constraints) is in [PRODUCT.md](PRODUCT.md).

## Build plan progress

This project follows the staged build plan in [PLAN.md](PLAN.md), one chapter at a time. **Chapters 1 (the naive end-to-end pipeline), 2 (role-based access control at retrieval time), 3 (structured data behind tools), 4 (an agent loop that routes between tools and document search), and 5 (tokenizing structured data - employee identity, salary, leave balance - before it reaches the model) are complete.** Chapter 6 (latency - measuring and cutting down model calls) is next. Concrete gaps found but not yet fixed are tracked in [TODO.md](TODO.md).
