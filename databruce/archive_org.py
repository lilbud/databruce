import asyncio
import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from internetarchive import get_item, search_items
from psycopg.rows import dict_row

load_dotenv()

with Path.open(Path(Path(__file__).parent, "scripts", "uploaded.json")) as file:
    links = dict(json.load(file))


async def load_db() -> psycopg.Connection:
    """Load DB and return connection."""
    return psycopg.connect(
        conninfo=os.getenv("LOCAL_DB_URL"),
        row_factory=dict_row,
    )


async def get_list_from_archive() -> None:
    """b,."""
    with await load_db() as conn:
        for i in search_items("collection:radionowhere"):
            event_id = get_item(i["identifier"]).metadata["databruce_id"]
            print(event_id)

            conn.execute(
                """INSERT INTO archive_links (event_id, archive_url) VALUES (%s, %s)""",
                (event_id, i["identifier"]),
            )


async def get_json_list() -> None:
    """."""
    with await load_db() as conn:
        for event, identifier in links.items():
            if isinstance(identifier, list):
                for i in identifier:
                    conn.execute(
                        """INSERT INTO archive_links (event_id, archive_url)
                            VALUES (%s, %s)""",
                        (event, f"https://archive.org/details/{i}"),
                    )
            else:
                conn.execute(
                    """INSERT INTO archive_links (event_id, archive_url)
                        VALUES (%s, %s)""",
                    (event, f"https://archive.org/details/{identifier}"),
                )


asyncio.run(get_json_list())
