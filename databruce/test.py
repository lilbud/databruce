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


def get_band_id(url: str, cur: psycopg.cursor) -> int:
    """Get band id for a given band url."""
    try:
        res = cur.execute(
            """SELECT id FROM bands WHERE brucebase_url = %s""",
            (url,),
        ).fetchone()

        return res["id"]
    except (TypeError, psycopg.OperationalError):
        return None


def get_relation_id(url: str, cur: psycopg.cursor) -> int:
    """Get id for a given relation url."""
    try:
        res = cur.execute(
            """SELECT id FROM relations WHERE brucebase_url = %s""",
            (url,),
        ).fetchone()

        return res["id"]
    except (TypeError, psycopg.OperationalError):
        return None


def get_note(item: Tag) -> str:
    """Get note attached to an onstage li item."""
    try:
        return item.span.text.lower().strip("()")
    except (TypeError, psycopg.OperationalError):
        return None


async def main():
    content = Path(Path(__file__).parent, "test.html").read_text()

    soup = bs4(content, "lxml")
    onstage = []

    with load_db() as conn, conn.cursor() as cur:
        for subgroup in soup.find_all("ul"):
            for link in subgroup.find_all("li"):
                try:
                    for member in link.ul.find_all("li"):
                        relation = get_relation_id(member.a["href"], cur)
                        band = get_band_id(subgroup.a["href"], cur)
                        note = get_note(member)

                        if relation not in [k[0] for k in onstage]:
                            onstage.append([relation, band, note])
                except AttributeError:
                    relation = get_relation_id(link.a["href"], cur)
                    band = get_band_id(link.a["href"], cur)
                    note = get_note(link)

                    if relation not in [k[0] for k in onstage]:
                        onstage.append([relation, band, note])

        print(onstage)

    # for i in soup.find_all("li"):
    #     group = None

    #     if i.find("ul"):
    #         group = get_band_id(i.a["href"])

    #         for j in i.find("ul").find_all("li"):
    #             member = [get_relation_id(j.a["href"]), group]

    #             if member not in onstage:
    #                 onstage.append(member)

    #     else:
    #         member = [get_relation_id(i.a["href"]), None]

    #         if member not in onstage:
    #             onstage.append(member)

    # print(onstage)


asyncio.run(main())
