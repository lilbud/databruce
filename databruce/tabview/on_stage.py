"""Functions to handle the "On Stage" tab of an event page."""

import re

import psycopg
from bs4 import Tag
from slugify import slugify


def get_band_id(url: str, cur: psycopg.cursor) -> int:
    """Get band id for a given band url."""
    try:
        res = cur.execute(
            """SELECT id FROM bands WHERE brucebase_url = %s""",
            (url,),
        ).fetchone()

        return res["id"]
    except (TypeError, psycopg.OperationalError):
        return None


def get_relation_id(url: str, cur: psycopg.cursor) -> int:
    """Get id for a given relation url."""
    try:
        res = cur.execute(
            """SELECT id FROM relations WHERE brucebase_url = %s""",
            (url,),
        ).fetchone()

        return res["id"]
    except (TypeError, psycopg.OperationalError):
        return None


def get_note(item: Tag) -> str:
    """Get note attached to an onstage li item."""
    try:
        return item.span.text.lower().strip("()")
    except (TypeError, psycopg.OperationalError):
        return None


async def get_relation_id(
    relation_url: str,
    cur: psycopg.AsyncCursor,
) -> int:
    """Return the relation_id for the given relation_url."""
    res = await cur.execute(
        """SELECT id FROM "relations" WHERE brucebase_url=%s""",
        (relation_url,),
    )

    relation = await res.fetchone()

    return relation["id"]


async def get_relation_note(relation: Tag) -> str | None:
    """Return the note inside a list element."""
    try:
        return relation.span.text.lower().strip("()")
    except AttributeError:
        return None


async def get_onstage(
    tab_contents: Tag,
    event_id: str,
    cur: psycopg.AsyncCursor,
) -> None:
    """Get a list of those on stage at a given event."""
    onstage = []

    for subgroup in tab_contents.find_all("ul"):
        for link in subgroup.find_all("li"):
            try:
                for member in link.ul.find_all("li"):
                    relation = get_relation_id(member.a["href"], cur)
                    band = get_band_id(subgroup.a["href"], cur)
                    note = get_note(member)

                    if relation not in [k[0] for k in onstage]:
                        onstage.append([relation, band, note])

            except AttributeError:
                relation = get_relation_id(link.a["href"], cur)
                band = get_band_id(link.a["href"], cur)
                note = get_note(link)

                if relation not in [k[0] for k in onstage]:
                    onstage.append([relation, band, note])

    for item in onstage:
        try:
            await cur.execute(
                """INSERT INTO "onstage"
                    (event_id, relation_id, band_id, note)
                    VALUES (%(event)s, %(relation)s, %(band)s, %(note)s)
                    ON CONFLICT(event_id, relation_id) DO NOTHING""",
                {
                    "event": event_id,
                    "relation": item[0],
                    "band": item[1],
                    "note": item[2],
                },
            )

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)

    print(f"onstage table updated for {event_id}")
