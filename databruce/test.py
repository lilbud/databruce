"""File for testing random code/functions/ideas."""

import asyncio
import json
import random
import re
from datetime import datetime
from pathlib import Path

import dateparser
import enchant
import ftfy
import httpx
import musicbrainzngs
import pandas as pd
import psycopg
from bs4 import BeautifulSoup as bs4
from database.db import load_db
from dotenv import load_dotenv
from psycopg.rows import dict_row
from spellchecker import SpellChecker
from textblob import TextBlob, Word
from tools.parsing import html_parser
from tools.scraping import scraper

load_dotenv()

# df = pd.read_csv(Path(r"E:\Media\Music\Bootlegs\_other\Millard.csv"), encoding="cp1252")

# unique_artists = df["artist"].unique().tolist()
# generations = df["generation"].unique().tolist()
# unique_dates = df["date"].unique().tolist()
# unique_locations = df["venue"].unique().tolist()

# print(f"Unique Artists: {len(unique_artists)}")
# print("\nGenerations:\n" + "-" * 20)

# for g in generations:
#     print(f"{g}: {len(df.loc[df["generation"] == g])}")

# print(f"\nUnique Shows: {len(unique_dates)}")
# print(f"\nUnique Locations: {len(unique_locations)}")

res = httpx.get("https://www.wysterialane.org/goose-101-an-introduction-and-guide/")
soup = bs4(res.content, "lxml")

with httpx.Client() as client:
    response = client.get(
        "https://archive.org/advancedsearch.php?q=collection%3A%22radionowhere%22&fl[]=identifier&fl[]=databruce_id&sort[]=&sort[]=&sort[]=&rows=2000&page=1&output=json",
    )

    if response:
        for item in response.json()["response"]["docs"]:
            print(item)
