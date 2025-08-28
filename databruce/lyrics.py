import asyncio
import json
import os
import re
from pathlib import Path

import ftfy
import httpx
import psycopg
from bs4 import BeautifulSoup as bs4
from dotenv import load_dotenv
from lyricsgenius import Genius
from psycopg.rows import dict_row
from tools.scraping import scraper
from user_agent import generate_user_agent

load_dotenv()


def load_db() -> psycopg.Connection:
    """Load DB and return connection."""
    return psycopg.connect(
        conninfo=os.getenv("LOCAL_DB_URL"),
        row_factory=dict_row,
    )


def get_song(cur: psycopg.Cursor, title: str):
    return cur.execute(
        """SELECT id, category FROM songs WHERE lower(song_name) = %s AND original IS TRUE""",
        (title.lower(),),
    ).fetchone()


bruceid = 19041

with Path(
    r"C:\Users\bvw20\Documents\Software\Programming\Python\Projects\databruce\Lyrics_BruceSpringsteen.json",
).open() as f:
    file = json.load(f)


with load_db() as conn, conn.cursor() as cur:
    for song in file["songs"]:
        if (
            not re.search(
                r"\[|\(Live",
                song["title"],
            )
            and song["lyrics"]
        ):
            fixed = ftfy.fix_text(song["title"])

            song_info = get_song(cur, fixed)

            if song_info:
                id = song_info["id"]
                version = song_info["category"]
                lyrics = song["lyrics"]
                source = "genius"

                print(fixed)
                # print(lyrics)
                # print()

                # cur.execute(
                #     """INSERT INTO lyrics (song_id, version_info, source_info, lyrics) VALUES (%s, %s, %s, %s)""",
                #     (id, version, source, lyrics),
                # )


# title = file["songs"][0]["title"]
# lyrics = file["songs"][0]["lyrics"]

# print(title)
