"""Functions to handle the "On Stage" tab of an event page."""

import psycopg
from bs4 import Tag


async def get_band_id(url: str, name: str, cur: psycopg.AsyncCursor) -> int:
    """Get band id for a given band url."""
    try:
        res = await cur.execute(
            """SELECT id FROM bands WHERE brucebase_url = %s""",
            (url,),
        )

        band = await res.fetchone()
        return band["id"]
    except TypeError:
        await cur.execute(
            """INSERT INTO bands (brucebase_url, band_name) VALUES (%s, %s)""",
            (url, name),
        )

        res = await cur.execute(
            """SELECT id FROM bands WHERE brucebase_url = %s""",
            (url,),
        )

        band = await res.fetchone()
        return band["id"]


async def get_relation_id(url: str, name: str, cur: psycopg.AsyncCursor) -> int:
    """Get id for a given relation url."""
    try:
        res = await cur.execute(
            """SELECT id FROM relations WHERE brucebase_url = %s""",
            (url,),
        )

        relation = await res.fetchone()
        return relation["id"]
    except TypeError:  # relation doesn't exist
        await cur.execute(
            """INSERT INTO relations (brucebase_url, relation_name) VALUES (%s, %s)""",
            (url, name),
        )

        res = await cur.execute(
            """SELECT id FROM relations WHERE brucebase_url = %s""",
            (url,),
        )

        relation = await res.fetchone()
        return relation["id"]


async def get_note(item: Tag) -> str:
    """Get note attached to an onstage li item."""
    try:
        return item.span.text.lower().strip("()")
    except AttributeError:
        return None


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
                    relation = await get_relation_id(
                        member.a["href"],
                        member.a.get_text(),
                        cur,
                    )
                    band = await get_band_id(
                        subgroup.a["href"],
                        subgroup.a.get_text(),
                        cur,
                    )
                    note = await get_note(member)

            except AttributeError:
                relation = await get_relation_id(link.a["href"], link.a.get_text(), cur)
                band = await get_band_id(link.a["href"], link.a.get_text(), cur)
                note = await get_note(link)

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
