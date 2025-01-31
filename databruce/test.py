"""File for testing random code/functions/ideas."""

import asyncio
import re
from pathlib import Path

import httpx
import pandas as pd
from database.db import load_db
from dotenv import load_dotenv
from tools.scraping import scraper

load_dotenv()
from bs4 import BeautifulSoup as bs4

df = pd.read_csv(
    Path(r"C:\Users\bvw20\Documents\Personal\Databruce Project\sign requests.csv"),
)

with load_db() as conn:
    cur = conn.cursor()

    fix = []
    print(df)

    for row in df.itertuples():
        cur.execute(
            """UPDATE setlists SET sign_request = true WHERE event_id = %s and song_id = %s AND set_name <> ALL(ARRAY['Soundcheck', 'Rehearsal'])""",
            (row.event, row.song),
        )
