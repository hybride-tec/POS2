# db.py
"""PostgreSQL connection helper, shared by pos_logic.py and init_db.py."""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Open a new database connection using settings from the environment."""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME", "pos_db"),
        user=os.environ.get("DB_USER", "pos_user"),
        password=os.environ.get("DB_PASSWORD", ""),
    )


def dict_cursor(conn):
    """A cursor that returns rows as dictionaries instead of tuples."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
