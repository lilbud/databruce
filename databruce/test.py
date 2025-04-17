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
    response = await scraper.post("18072044")

    # duplicate song ids which redirect
    ignore = [
        "/song:born-in-the-usa",
        "/song:land-of-1-000-dances",
        "/song:land-of-1000-dances",
        "/song:deportee-plane-wreck-at-los-gatos",
    ]

    if response:
        soup = bs4(response, "lxml")

        songs = await html_parser.get_all_links(soup, "/song:")

        links = [
            [link["url"], link["text"]] for link in songs if link["url"] not in ignore
        ]

        print(links)


asyncio.run(main())
