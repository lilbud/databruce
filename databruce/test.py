"""File for testing random code/functions/ideas."""

import asyncio

import psycopg
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
            31607,
        ]
        member_list = [
            "Robbin Thompson",
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


add_guests_to_setlist()
