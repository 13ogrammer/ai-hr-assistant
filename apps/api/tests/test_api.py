"""Tests for the HTTP layer only.

/ask depends on a live DB, a loaded embedding model, and a real (paid)
OpenAI call - none of that belongs in these tests. generate_answer() is
mocked so these tests check what this layer actually owns: request
validation, response shape, and correct wiring. The real pipeline is
covered by tests/test_retrieve.py (real DB) and manual verification
against the real OpenAI API.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_users_returns_the_fake_directory():
    response = client.get("/users")
    assert response.status_code == 200
    roles = {user["role"] for user in response.json()}
    assert roles == {"employee", "manager", "hr"}


def test_ask_passes_through_the_answer_and_sources_from_generate_answer():
    with patch("api.routes.generate_answer", return_value=("answer", ["a.md", "b.md"])):
        response = client.post("/ask", json={"question": "question", "user_id": "maya.chen"})

    assert response.json() == {"answer": "answer", "sources": ["a.md", "b.md"]}


def test_ask_passes_the_resolved_user_to_generate_answer():
    with patch("api.routes.generate_answer", return_value=("answer", [])) as mock_generate:
        client.post("/ask", json={"question": "question", "user_id": "tom.richards"})

    args, _ = mock_generate.call_args
    assert args[0] == "question"
    assert args[1].id == "tom.richards"
    assert args[1].role == "manager"


def test_ask_rejects_unknown_user_id():
    response = client.post("/ask", json={"question": "question", "user_id": "not.a.real.user"})
    assert response.status_code == 400


def test_ask_rejects_missing_question():
    response = client.post("/ask", json={"user_id": "maya.chen"})
    assert response.status_code == 422


def test_ask_rejects_non_string_question():
    response = client.post("/ask", json={"question": 12345, "user_id": "maya.chen"})
    assert response.status_code == 422


def test_ask_rejects_missing_user_id():
    response = client.post("/ask", json={"question": "question"})
    assert response.status_code == 422
