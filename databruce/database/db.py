import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv()

DATABASE_URL = os.getenv("LOCAL_DB_URL")
pool = ConnectionPool(conninfo=DATABASE_URL, open=False)


def load_db() -> psycopg.Connection:
    """Load DB and return connection."""
    return psycopg.connect(
        conninfo=DATABASE_URL,
        row_factory=dict_row,
    )  # ty:ignore[no-matching-overload]
