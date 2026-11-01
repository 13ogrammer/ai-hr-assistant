"""Tests for the HTTP layer only.

/ask depends on a live DB, a loaded embedding model, and a real (paid)
OpenAI call - none of that belongs in these tests. retrieve() and
generate_answer() are mocked so these tests check what this layer
actually owns: request validation, response shape, and correct wiring.
The real pipeline is covered by tests/test_retrieve.py (real DB) and
manual verification against the real OpenAI API.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app
from models.chunk import RetrievedChunk

client = TestClient(app)


def make_chunk(source="policy.md", chunk_index=0, content="text", distance=0.1):
    return RetrievedChunk(source=source, chunk_index=chunk_index, content=content, distance=distance)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ask_deduplicates_and_sorts_sources():
    chunks = [make_chunk(source="b.md"), make_chunk(source="a.md"), make_chunk(source="a.md")]
    with (
        patch("api.routes.retrieve", return_value=chunks),
        patch("api.routes.generate_answer", return_value="answer"),
    ):
        response = client.post("/ask", json={"question": "question"})

    assert response.json()["sources"] == ["a.md", "b.md"]


def test_ask_rejects_missing_question():
    response = client.post("/ask", json={})
    assert response.status_code == 422


def test_ask_rejects_non_string_question():
    response = client.post("/ask", json={"question": 12345})
    assert response.status_code == 422
