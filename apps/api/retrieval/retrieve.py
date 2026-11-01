"""Embed a question and find the most similar stored chunks.

Run with: uv run python -m retrieval.retrieve "your question here"
"""

import sys

from models.chunk import RetrievedChunk
from shared.db import get_connection
from shared.embeddings import get_embedding_model

TOP_K = 5


def retrieve(question: str, role: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
    """Retrieve the top_k chunks most similar to question, restricted to those
    role is allowed to see.

    role must come from the caller's verified identity (the session/request,
    via shared.users), never parsed out of the question text - the filter
    below is a SQL WHERE clause, not a prompt instruction, so there's nothing
    for a cleverly worded question to talk its way around.
    """
    model = get_embedding_model()
    [query_embedding] = list(model.query_embed([question]))

    conn = get_connection()
    rows = conn.execute(
        """
        SELECT source, chunk_index, content, embedding <=> %s AS distance, access_level
        FROM chunks
        WHERE %s = ANY(allowed_roles)
        ORDER BY distance
        LIMIT %s
        """,
        (query_embedding, role, top_k),
    ).fetchall()
    conn.close()

    return [
        RetrievedChunk(
            source=source,
            chunk_index=chunk_index,
            content=content,
            distance=distance,
            access_level=access_level,
        )
        for source, chunk_index, content, distance, access_level in rows
    ]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit('Usage: uv run python -m retrieval.retrieve <role> "your question here"')
    role = sys.argv[1]
    question = " ".join(sys.argv[2:])
    print(f"Role: {role}")
    print(f"Question: {question}\n")
    for chunk in retrieve(question, role):
        print(f"[distance={chunk.distance:.4f}] {chunk.source} (chunk {chunk.chunk_index})")
        print(chunk.content[:200].replace("\n", " "))
        print()
