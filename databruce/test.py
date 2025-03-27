"""File for testing random code/functions/ideas."""

import asyncio
import re
from pathlib import Path

from database.db import load_db
from dotenv import load_dotenv

load_dotenv()
from bs4 import BeautifulSoup as bs4

# def get_setlist_id(event: str, song: str, cur: psycopg.Cursor):
#     id = cur.execute(
#         """SELECT id FROM setlists WHERE event_id = %s AND song_id = %s
#         AND set_name = ANY(ARRAY['Show', 'Set 1', 'Set 2', 'Encore', 'Pre-Show', 'Rehearsal'])""",
#         (event, song),
#     ).fetchone()
#     try:
#         return id["id"]
#     except TypeError:
#         print(event, song)

with load_db() as conn:
    cur = conn.cursor()
    venues = []

    events = cur.execute(
        """SELECT brucebase_url FROM events WHERE venue_id IS NULL""",
    ).fetchall()

    for e in events:
        url = re.sub(r"^\/.*\:\d{4}-\d{2}-\d{2}[a-z]?-", "", e["brucebase_url"])

        v_id = cur.execute(
            """SELECT id FROM venues WHERE brucebase_url = %s""",
            (url,),
        ).fetchone()

        if v_id:
            cur.execute(
                """UPDATE events SET venue_id = %s WHERE brucebase_url = %s""",
                (v_id["id"], e["brucebase_url"]),
            )
