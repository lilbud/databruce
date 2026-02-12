"""File for testing random code/functions/ideas."""

import asyncio
import calendar
import datetime
import io
import json
import random
import re
import time
from pathlib import Path

import ftfy

# import html_to_markdown
import httpx

# import nameparser
import pandas as pd
import psycopg
import slugify
from bs4 import BeautifulSoup as bs4
from bs4 import Tag
from database import db
from dotenv import load_dotenv

# from html2text import html2text
# from justhtml import JustHTML
# from markdownify import markdownify as md
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from tools.scraping import scraper
from venues import venue_parser

load_dotenv()


def get_rel_id(name: str, cur: psycopg.Cursor) -> int:
    return cur.execute(
        """SELECT id FROM relations WHERE relation_name = %s""",
        (name,),
    ).fetchone()["id"]


def get_event(id: int, cur: psycopg.Cursor) -> int:  # noqa: D103
    return cur.execute(
        """SELECT event_id FROM setlists WHERE id = %s""",
        (id,),
    ).fetchone()["event_id"]


def add_guests_to_setlist():
    with db.load_db() as conn, conn.cursor() as cur:
        setlist = [
            42800,
        ]
        member_list = [
            918,
            944,
            710,
            233,
            999,
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


def manual_setlist_add():
    setlist = []

    with db.load_db() as conn:
        cur = conn.cursor()
        set_name = "Rehearsal"
        event_id = "20250514-01"

        for index, song in enumerate(setlist, start=1):
            song_id = cur.execute(
                """SELECT id FROM songs WHERE lower(song_name) = %s""",
                (song.lower(),),
            ).fetchone()["id"]

            cur.execute(
                """INSERT INTO setlists (event_id, set_name, song_num, song_id)
                VALUES (%s, %s, %s, %s)""",
                (event_id, set_name, index, song_id),
            )


def manual_onstage():
    onstage = [
        [1358, 130],
        [1190, 130],
        [384, 130],
        [7, 130],
        [73, 130],
        [1263, 131],
        [1464, 131],
        [559, 131],
        [104, 131],
        [796, 129],
        [1766, 129],
        [302, 129],
        [1309, 129],
        [1826, 129],
        [654, 129],
        [1447, 129],
        [1691, 129],
        [255, None],
    ]

    with db.load_db() as conn:
        cur = conn.cursor()
        event_id = "20250514-01"

        for member in onstage:
            cur.execute(
                """INSERT INTO onstage (event_id, relation_id, band_id)
                VALUES (%s, %s, %s)""",
                (event_id, member[0], member[1]),
            )


def format_song_note(note: Tag) -> str:
    try:
        return re.sub(r"^[\s\(\)]|[\s\(\)]$", "", note.get_text())
    except AttributeError:
        return None


def get_song_id(url: Tag, cur: psycopg.Cursor) -> int:
    url = url.get("href")

    return cur.execute(
        """SELECT id FROM songs WHERE brucebase_url = %s""",
        (url,),
    ).fetchone()["id"]


# with Path.open(Path(Path(__file__).parent, "test.html")) as file:
#     soup = bs4("\n".join(file.readlines()), "lxml")
#     set_names = soup.select("p > strong")
#     setlist = {}
#     # setlist format: some have ul/ol blocks separated by P elements which are the name of the set. Usually only soundcheck/rehearsal/pre-show and show

#     with db.load_db() as conn:
#         cur = conn.cursor()

#         song_num = 1

#         for set in set_names:
#             set_name = set.get_text()

#             for item in set.find_next(["ul", "ol"]).find_all("li"):
#                 segue = False
#                 if len(item.find_all("a")) == 1:
#                     song_id = get_song_id(item.find("a"), cur)
#                     song_note = format_song_note(item.span)

#                     print(set_name, song_num, song_id, song_note, segue)
#                     song_num += 1
#                 elif len(item.find_all("a")) > 1 and not item.find(["ul", "ol"]):
#                     sequence = item.find_all("a")
#                     for seq_index, song in enumerate(sequence):
#                         song_id = get_song_id(song, cur)
#                         song_note = format_song_note(item.span)
#                         segue = False

#                         # check song segue
#                         if seq_index <= len(sequence) - 2:
#                             segue = True

#                         print(set_name, song_num, song_id, song_note, segue)
#                         song_num += 1


def filehost(link: str) -> str:
    if "mega.nz" in link:
        return f"[MEGA]({link})"
    if "wetransfer.com" in link:
        return f"[WeTransfer]({link})"

    return None


# def main():
#     headers = {
#         "User-Agent": generate_user_agent(),
#         "Cookie": "wikidot_token7=0",
#     }
#     save = Path(
#         r"C:\Users\bvw20\Pictures\Graphic_Design\Projects\Music\Bootleg_Covers\bruce\_images\1981\1981-07-02",
#     )
#     save.mkdir(exist_ok=True)
#     base = "https://www.app.com"
#     with httpx.Client() as client:
#         url = r"https://www.app.com/picture-gallery/entertainment/2025/08/13/bruce-springsteen-and-the-e-street-band-perform-at-the-brendan-byrne-arena-1981/85242117007/"
#         r = client.get(
#             url=url,
#         )
#         soup = bs4(r.content, "lxml")
#         with Path(save, "info.txt").open("w") as f:
#             f.write(f"photos from here: {url}")
#         for i in soup.find_all("img"):
#             img = re.sub(r"\?.*", "", i["src"])
#             filename = re.sub(r"\d{11}-", "", img.split("/")[-1])
#             photog = slugify.slugify(
#                 re.sub(r"\/.*", "", i.parent.next_sibling.next_sibling),
#             )
#             # print(photog, filename)
#             img_data = client.get(f"{base}{img}")
#             if img_data:
#                 if not Path(save, f"{photog}_{filename}").exists():
#                     print(filename)
#                     with Path(save, f"{photog}_{filename}").open("wb") as file:
#                         file.write(img_data.content)
#                 else:
#                     print(f"{filename} exists, skipping")
#             time.sleep(0.5)

with db.load_db() as conn, conn.cursor() as cur:
    file = Path(r"C:\Users\bvw20\Desktop\onstage.csv").read_text()

    for line in file.split("\n")[1:]:
        id = event_id = relation_id = band_id = updated = created = uuid = None

        try:
            id, event_id, relation_id, band_id, updated, created, uuid = line.split(",")
            # print(event_id, relation_id, band_id)
            print("---")

            try:
                event = cur.execute(
                    """SELECT id FROM events WHERE event_id = %s""",
                    (event_id,),
                ).fetchone()["id"]

                if band_id == "":
                    band_id = None

                if created in ("", "t", "f"):
                    created = updated

                if band_id in [
                    451,
                    437,
                    30,
                    137,
                    38,
                    48,
                    50,
                    453,
                    444,
                    59,
                    63,
                    70,
                    459,
                    427,
                    461,
                    462,
                    83,
                    450,
                    117,
                    125,
                    126,
                    447,
                    419,
                    157,
                    163,
                    452,
                    204,
                ]:
                    print(event_id, relation_id, band_id)
                    cur.execute(
                        """INSERT INTO onstage (event_id, relation_id, band_id, created_at) VALUES (%s, %s, %s, %s) on conflict (event_id, relation_id, band_id) do nothing""",
                        (event, relation_id, band_id, created),
                    )
            except TypeError:
                pass
        except ValueError:
            pass
