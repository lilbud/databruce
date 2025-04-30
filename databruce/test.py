"""File for testing random code/functions/ideas."""

import asyncio
import datetime
import re
import time
from pathlib import Path

import ftfy
import numpy as np
import pandas as pd
import psycopg
import slugify
from bs4 import BeautifulSoup as bs4
from bs4 import Tag
from database.db import load_db
from dotenv import load_dotenv
from psycopg.rows import dict_row
from titlecase import titlecase
from tools.parsing import html_parser
from tools.scraping import scraper

load_dotenv()


def get_rel_id(name: str, cur: psycopg.Cursor) -> int:
    return cur.execute(
        """SELECT id FROM relations WHERE relation_name = %s""",
        (name,),
    ).fetchone()["id"]


def get_event(id: int, cur: psycopg.Cursor) -> int:
    return cur.execute(
        """SELECT event_id FROM setlists WHERE id = %s""",
        (id,),
    ).fetchone()["event_id"]


def main():
    with load_db() as conn, conn.cursor() as cur:
        setlist = [
            63518,
        ]
        member_list = [
            "Darlene Love",
            "Nora Guthrie",
            "Emmylou Harris",
            "Patti Scialfa",
            "Tom Morello",
            "John Fogerty",
            "Jackson Browne",
            "Steven Van Zandt",
            "Nils Lofgren",
        ]

        for s in setlist:
            event = get_event(s, cur)
            for member in member_list:
                id = member
                if isinstance(member, str):
                    id = get_rel_id(member, cur)

                cur.execute(
                    """INSERT INTO guests (event_id, setlist_id, guest_id)
                    VALUES (%(event)s, %(setlist)s, %(guest)s)
                    ON CONFLICT(setlist_id, guest_id) DO NOTHING
                    """,
                    {"event": event, "setlist": s, "guest": id},
                )


main()
