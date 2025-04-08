"""File for testing random code/functions/ideas."""

import asyncio
import re
import time
from pathlib import Path

import ftfy
import numpy as np
import pandas as pd
import slugify
from database.db import load_db
from dotenv import load_dotenv
from psycopg.rows import dict_row
from titlecase import titlecase
from tools.parsing import html_parser

load_dotenv()
from bs4 import BeautifulSoup as bs4
from tools.scraping import scraper


async def main():
    response = await scraper.get(
        "http://brucebase.wikidot.com/interview:2020-04-08-siriusxm-studio-new-york-city-ny",
    )

    if response:
        soup = bs4(response.text, "lxml")

        title = re.search(r"(.*)\s-\sBrucebase Wiki", soup.title.get_text())[1]
        venue_url = soup.select_one(
            "#page-content > p:nth-child(3) > a:nth-child(2)",
        ).get("href")
        event_date = re.search(r"\d{4}-\d{2}-\d{2}", title)[0]
        venue_id = re.sub("^/.*:", "", venue_url)

        print(venue_id)
