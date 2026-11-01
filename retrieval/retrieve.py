"""Embed a question and find the most similar stored chunks.

Run with: uv run python -m retrieval.retrieve "your question here"
"""

import sys

from models.chunk import RetrievedChunk
from shared.db import get_connection
from shared.embeddings import get_embedding_model

TOP_K = 5


def retrieve(question: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
    model = get_embedding_model()
    [query_embedding] = list(model.query_embed([question]))

    conn = get_connection()
    rows = conn.execute(
        """
        SELECT source, chunk_index, content, embedding <=> %s AS distance
        FROM chunks
        ORDER BY distance
        LIMIT %s
        """,
        (query_embedding, top_k),
    ).fetchall()
    conn.close()

    return [
        RetrievedChunk(source=source, chunk_index=chunk_index, content=content, distance=distance)
        for source, chunk_index, content, distance in rows
    ]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: uv run python -m retrieval.retrieve "your question here"')
    question = " ".join(sys.argv[1:])
    print(f"Question: {question}\n")
    for chunk in retrieve(question):
        print(f"[distance={chunk.distance:.4f}] {chunk.source} (chunk {chunk.chunk_index})")
        print(chunk.content[:200].replace("\n", " "))
        print()
