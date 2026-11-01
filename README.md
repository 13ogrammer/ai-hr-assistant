# HR Assistant

A monorepo with two independently deployable apps:

- **[apps/api](apps/api)** — the FastAPI backend: ingestion, retrieval, generation, and the `/ask` endpoint. See its own README for setup and running instructions.
- **[apps/web](apps/web)** — a Vite + React frontend scaffold, separate from `apps/api`'s own tiny built-in UI (`apps/api/static/index.html`). Not yet wired up to call the backend.

Each app has its own dependency manager and lockfile (`uv`/`pyproject.toml` for the API, `npm`/`package.json` for the web app) and is meant to be run and deployed independently.
