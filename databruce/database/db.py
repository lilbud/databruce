import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

load_dotenv()

DATABASE_URL = os.getenv("LOCAL_DB_URL")
pool = AsyncConnectionPool(conninfo=DATABASE_URL, open=False)


def reset_serials(conn: psycopg.Connection) -> None:
    """Fix the IDs being way out of order."""
    """Found that the IDs increment whether an insert is done or not. Meaning the IDs
    will have sometimes 10k values between rows"""
    conn.execute("""
        SELECT setval(pg_get_serial_sequence('bands', 'id'), coalesce(MAX(id), 1))
        from bands;

        SELECT setval(pg_get_serial_sequence('cities', 'id'), coalesce(MAX(id), 1))
        from cities;

        SELECT setval(pg_get_serial_sequence('states', 'id'), coalesce(MAX(id), 1))
        from states;

        SELECT setval(pg_get_serial_sequence('countries', 'id'), coalesce(MAX(id), 1))
        from countries;

        SELECT setval(pg_get_serial_sequence('venues', 'id'), coalesce(MAX(id), 1))
        from venues;

        SELECT setval(pg_get_serial_sequence('relations', 'id'), coalesce(MAX(id), 1))
        from relations;

        SELECT setval(pg_get_serial_sequence('archive_links', 'id'), coalesce(MAX(id), 1))
        from archive_links;

        SELECT setval(pg_get_serial_sequence('covers', 'id'), coalesce(MAX(id), 1))
        from covers;

        SELECT setval(pg_get_serial_sequence('bootlegs', 'id'), coalesce(MAX(id), 1))
        from bootlegs;

        SELECT setval(pg_get_serial_sequence('tour_legs', 'id'), coalesce(MAX(id), 1))
        from tour_legs;

        SELECT setval(pg_get_serial_sequence('songs', 'id'), coalesce(MAX(id), 1))
        from songs;

        SELECT setval(pg_get_serial_sequence('setlists', 'id'), coalesce(MAX(id), 1))
        from setlists;
    """)


def load_db() -> psycopg.Connection:
    """Load DB and return connection."""
    conn = psycopg.connect(
        conninfo=DATABASE_URL,
        row_factory=dict_row,
    )

    reset_serials(conn)

    return conn
