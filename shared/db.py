import os

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

load_dotenv()

EMBEDDING_DIM = 384


def get_connection() -> psycopg.Connection:
    conn = psycopg.connect(os.environ["DATABASE_URL"])
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.commit()
    register_vector(conn)
    return conn


def ensure_schema(conn: psycopg.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            source TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding VECTOR({EMBEDDING_DIM}) NOT NULL
        )
        """
    )
    conn.commit()
