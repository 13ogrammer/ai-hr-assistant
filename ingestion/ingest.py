"""Chunk every doc in docs/*.md, embed each chunk, and store it in Postgres.

Run with: uv run python -m ingestion.ingest
"""

import pathlib
import re

from shared.db import ensure_schema, get_connection
from shared.embeddings import get_embedding_model

DOCS_DIR = pathlib.Path(__file__).resolve().parent.parent / "docs"
MAX_CHUNK_CHARS = 1000

HEADING_PATTERN = re.compile(r"^#{1,6}\s.*$", re.MULTILINE)


def split_into_sections(text: str) -> list[str]:
    """Split markdown text at each heading line, so each section is one heading
    plus the content under it, up to the next heading.

    A heading with no body of its own - only child subsections follow it
    immediately - gets folded into the next section instead of becoming a
    near-empty chunk that contains nothing but a section title."""
    matches = list(HEADING_PATTERN.finditer(text))
    if not matches:
        return [text]

    raw_sections = []
    if matches[0].start() > 0:
        preamble = text[: matches[0].start()]
        if preamble.strip():
            raw_sections.append(preamble)

    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        raw_sections.append(text[match.start() : end])

    sections = []
    pending = ""
    for section in raw_sections:
        heading_match = HEADING_PATTERN.match(section)
        body = section[heading_match.end() :].strip() if heading_match else section.strip()
        if heading_match and not body:
            pending += section.strip() + "\n\n"
            continue
        sections.append(pending + section if pending else section)
        pending = ""
    if pending:
        sections.append(pending.strip())

    return sections


def _pack_paragraphs(text: str, max_chars: int) -> list[str]:
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


def chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Chunk markdown text section by section, so a chunk never spans more
    than one heading's worth of content - unrelated topics never get mixed
    into the same chunk, even if together they'd fit under max_chars."""
    chunks = []
    for section in split_into_sections(text):
        chunks.extend(_pack_paragraphs(section, max_chars))
    return chunks


def main() -> None:
    model = get_embedding_model()

    conn = get_connection()
    ensure_schema(conn)
    conn.execute("DELETE FROM chunks")  # re-running this script should be idempotent

    for doc_path in sorted(DOCS_DIR.glob("*.md")):
        text = doc_path.read_text()
        chunks = chunk_text(text)
        embeddings = model.passage_embed(chunks)

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
