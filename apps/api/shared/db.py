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
            embedding VECTOR({EMBEDDING_DIM}) NOT NULL,
            access_level TEXT NOT NULL,
            allowed_roles TEXT[] NOT NULL
        )
        """
    )
    conn.commit()


def ensure_employees_schema(conn: psycopg.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            manager_name TEXT,
            salary INTEGER NOT NULL,
            leave_balance_days DOUBLE PRECISION NOT NULL
        )
        """
    )
    # ADD COLUMN IF NOT EXISTS so a table created before `title` existed still
    # picks it up - no migration framework yet, so this is the simplest way
    # ensure_employees_schema stays idempotent for an already-running DB.
    conn.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS title TEXT NOT NULL DEFAULT ''")
    conn.commit()
