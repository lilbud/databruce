"""File for testing random code/functions/ideas."""

import asyncio
import re
from datetime import datetime

import httpx
import psycopg
from bs4 import BeautifulSoup as bs4
from database import db
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
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
