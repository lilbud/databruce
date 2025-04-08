"""File for testing random code/functions/ideas."""

import asyncio
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
import slugify
from database.db import load_db
from dotenv import load_dotenv
from titlecase import titlecase
from tools.parsing import html_parser

load_dotenv()
from bs4 import BeautifulSoup as bs4
from tools.scraping import scraper


async def main():
    response = await scraper.get(
        "http://brucebase.wikidot.com/ott:arabian-nights",
    )

    if response:
        soup = bs4(response.text, "lxml")

        table = soup.select_one("#page-content > table:nth-child(2)")
        description = soup.select_one("#page-content > p:nth-child(3)")

        df = pd.read_html(str(table))[0]
        df.columns = ["title", "time", "release"]

        for i in df.itertuples():
            print(i.release)


async def ott_key():
    response = await scraper.get("http://brucebase.wikidot.com/stats:on-the-tracks-key")

    soup = bs4(response.text, "lxml")

    table1 = soup.select_one("#page-content > table:nth-child(5)")
    table2 = soup.select_one("#page-content > table:nth-child(7)")

    df1 = pd.read_html(str(table1))[0]
    df2 = pd.read_html(str(table2))[0]

    df1.columns = ["key", "title", "label", "carrier"]
    df2.columns = ["key", "title", "label", "carrier"]

    full = pd.concat([df1, df2], ignore_index=True)

    print(full)

    full.to_csv("ott_key.csv")

    # print(df2)


asyncio.run(ott_key())
