import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from internetarchive import search_items
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

load_dotenv()

with Path.open(Path(Path(__file__).parent, "scripts", "uploaded.json")) as file:
    links = dict(json.load(file))


async def get_list_from_archive() -> None:
    """b,."""
    return [i["identifier"] for i in search_items("collection:radionowhere")]


async def load_db() -> psycopg.Connection:
    """Load DB and return connection."""
    return psycopg.connect(
        conninfo=os.getenv("LOCAL_DB_URL"),
        row_factory=dict_row,
    )


async def get_recent_archives(pool: AsyncConnectionPool) -> None:
    """."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        for event, link in links.items():
            print(event)
            print(link)
            cur.execute(
                """INSERT INTO "archive_links" (event_id, archive_url)
                    VALUES (%s, %s)""",
                (event, link),
            )
