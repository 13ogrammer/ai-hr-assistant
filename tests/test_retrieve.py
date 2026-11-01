"""Integration tests for retrieve().

These need Postgres running (docker compose up -d) with the docs already
ingested (uv run python -m ingestion.ingest) - they hit the real database
and the real embedding model, unlike tests/test_ingest.py.
"""

from retrieval.retrieve import retrieve


def test_returns_requested_number_of_chunks():
    chunks = retrieve("How many days of annual leave do I get?", top_k=3)
    assert len(chunks) == 3


def test_relevant_question_retrieves_the_right_policy_doc():
    chunks = retrieve("How many days of annual leave do I get?", top_k=5)
    sources = {chunk.source for chunk in chunks}
    assert "02_ANNUAL_LEAVE_POLICY.md" in sources


def test_results_are_sorted_by_ascending_distance():
    chunks = retrieve("What is the bereavement leave policy?", top_k=5)
    distances = [chunk.distance for chunk in chunks]
    assert distances == sorted(distances)


def test_irrelevant_question_still_returns_chunks():
    # Known limitation, not a feature: there's no relevance threshold yet,
    # so a question with no real answer anywhere in the docs still returns
    # top_k chunks instead of signalling "I don't know." Chapter 7
    # (citations + a relevance threshold) is what fixes this.
    chunks = retrieve("What is the airspeed velocity of an unladen swallow?", top_k=5)
    assert len(chunks) == 5
