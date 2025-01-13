import asyncio
import json
import os
from pathlib import Path

import httpx
import psycopg
from dotenv import load_dotenv
from internetarchive import get_files, get_item, search_items
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

load_dotenv()


async def get_list_from_archive(pool: AsyncConnectionPool) -> None:
    """b,."""
    items = []

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://archive.org/advancedsearch.php?q=collection%3A%22radionowhere%22&fl[]=identifier&fl[]=databruce_id&sort[]=&sort[]=&sort[]=&rows=2000&page=1&output=json",
        )

        if response:
            items = [
                [
                    item["databruce_id"],
                    f"https://archive.org/details/{item["identifier"]}",
                ]
                for item in response.json()["response"]["docs"]
            ]

    # print(items)
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.executemany(
            """INSERT INTO archive_links (event_id, archive_url) VALUES (%s, %s)
                ON CONFLICT(event_id, archive_url) DO NOTHING RETURNING *""",
            (items),
        )
