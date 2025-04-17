"""File for testing random code/functions/ideas."""

import asyncio
import datetime
import re
import time
from pathlib import Path

import ftfy
import numpy as np
import pandas as pd
import slugify
from bs4 import BeautifulSoup as bs4
from database.db import load_db
from dotenv import load_dotenv
from psycopg.rows import dict_row
from titlecase import titlecase
from tools.parsing import html_parser
from tools.scraping import scraper

load_dotenv()


async def main():
    response = await scraper.get(
        "https://archive.org/advancedsearch.php?q=collection%3A%22radionowhere%22&fl[]=identifier&fl[]=databruce_id&fl[]=publicdate&sort[]=publicdate+asc&sort[]=&sort[]=&rows=2000&page=1&output=json",
    )

    if response:
        with load_db() as conn:
            cur = conn.cursor()

            for item in response.json()["response"]["docs"]:
                event_id = item["databruce_id"]
                created_at = datetime.datetime.strptime(  # noqa: DTZ007
                    item["publicdate"],
                    "%Y-%m-%dT%H:%M:%SZ",
                )
                url = f"https://archive.org/details/{item['identifier']}"

                cur.execute(
                    """INSERT INTO archive_links (event_id, archive_url, created_at)
                    VALUES (%s, %s, %s) ON CONFLICT (event_id, archive_url) DO NOTHING""",
                    (event_id, url, created_at),
                )


asyncio.run(main())
