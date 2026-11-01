# HR Assistant

An AI assistant for employees and the HR team at a fictional company. It is intended to answer questions about leave and HR policies, employment contracts, salary information, and pending leave requests.

This project is under development. The current service is a FastAPI scaffold with a health-check endpoint; the HR assistant features are not implemented yet.

## Run locally

Requires Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run uvicorn main:app --reload
```

The service runs at `http://127.0.0.1:8000`. Check `http://127.0.0.1:8000/health` for a health status response.
