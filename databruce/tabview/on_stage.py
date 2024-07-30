"""Functions to handle the "On Stage" tab of an event page."""

import re

import psycopg
from bs4 import Tag


async def get_relation_name(
    relation_id: str,
    conn: psycopg.Connection,
) -> str | None:
    """Return the relation_name from the database for the given relation_id."""
    relation = conn.execute(
        """SELECT relation_name AS name FROM "relations" WHERE relation_id=%s""",
        (relation_id,),
    ).fetchone()

    try:
        return relation["name"]
    except IndexError:
        return None


async def get_relation_id(
    relation_url: str,
) -> str:
    """Return the relation_id for the given relation_url."""
    return re.sub("/relation:", "", relation_url)


async def get_relation_note(relation: Tag) -> str | None:
    """Return the note inside a list element."""
    try:
        return relation.span.text.lower().strip("()")
    except AttributeError:
        return None


async def get_onstage(
    tab_contents: Tag,
    event_url: str,
    cur: psycopg.AsyncCursor,
) -> None:
    """Get a list of those on stage at a given event."""
    results = {"onstage": []}

    res = await cur.execute(
        """SELECT event_id AS id FROM "events" WHERE brucebase_url=%s""",
        (event_url,),
    )

    event_id = await res.fetchone()

    for link_group in tab_contents.find_all("ul", recursive=False):
        for link in link_group.find_all("li", recursive=False):
            try:
                for m in link.ul.find_all("li"):
                    current = {
                        "event_id": event_id["id"],
                        "relation_id": await get_relation_id(m.a["href"]),
                        "band_id": await get_relation_id(link.a["href"]),
                        "note": await get_relation_note(link),
                    }

                    if current not in results["onstage"]:
                        results["onstage"].append(current)
            except AttributeError:
                current = {
                    "event_id": event_id["id"],
                    "relation_id": await get_relation_id(link.a["href"]),
                    "band_id": None,
                    "note": await get_relation_note(link),
                }

                if current not in results["onstage"]:
                    results["onstage"].append(current)

    for item in results["onstage"]:
        try:
            await cur.execute(
                """INSERT INTO "onstage"
                    (event_id, relation_id, band_id, note)
                    VALUES (%(event_id)s, %(relation_id)s, %(band_id)s, %(note)s)
                    ON CONFLICT(event_id, relation_id) DO NOTHING""",
                item,
            )

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)

    print(f"onstage table updated for {event_url}")
