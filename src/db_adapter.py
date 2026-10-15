"""PostgreSQL boundary: physical schema is private to this module."""
import os
import psycopg
from psycopg.rows import dict_row

def connection():
    return psycopg.connect(
        host=os.getenv("LEGACY_DB_HOST", "legacy-db"),
        port=os.getenv("LEGACY_DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"], user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"], connect_timeout=1,
        options="-c statement_timeout=1000 -c lock_timeout=500", row_factory=dict_row,
    )

def available():
    try:
        with connection() as db:
            db.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False
