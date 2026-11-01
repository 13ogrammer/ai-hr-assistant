"""Chunk every doc in docs/*.md, embed each chunk, and store it in Postgres.

Run with: uv run python -m ingestion.ingest
"""

import pathlib

from fastembed import TextEmbedding

from shared.db import ensure_schema, get_connection

DOCS_DIR = pathlib.Path(__file__).resolve().parent.parent / "docs"
MAX_CHUNK_CHARS = 1000


def chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Group paragraphs into chunks, each under max_chars, breaking on blank lines."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph
    if current:
        chunks.append(current)
    return chunks


def main() -> None:
    model = TextEmbedding()  # defaults to BAAI/bge-small-en-v1.5, 384-dim vectors

    conn = get_connection()
    ensure_schema(conn)
    conn.execute("DELETE FROM chunks")  # re-running this script should be idempotent

    for doc_path in sorted(DOCS_DIR.glob("*.md")):
        text = doc_path.read_text()
        chunks = chunk_text(text)
        embeddings = model.embed(chunks)

        for index, (content, embedding) in enumerate(zip(chunks, embeddings)):
            conn.execute(
                """
                INSERT INTO chunks (source, chunk_index, content, embedding)
                VALUES (%s, %s, %s, %s)
                """,
                (doc_path.name, index, content, embedding),
            )
        print(f"{doc_path.name}: {len(chunks)} chunks")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
