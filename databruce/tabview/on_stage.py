"""Functions to handle the "On Stage" tab of an event page."""

import re

import psycopg
import slugify
from bs4 import Tag


async def get_relation_id(
    relation_url: str,
    cur: psycopg.AsyncCursor,
) -> int:
    """Return the relation_id for the given relation_url."""
    url = re.sub("/relation:", "", relation_url)

    res = await cur.execute(
        """SELECT id FROM "relations" WHERE brucebase_url=%s""",
        (url,),
    )

    relation = await res.fetchone()

    try:
        return relation["id"]
    except (IndexError, TypeError):
        return None


async def get_relation_note(relation: Tag) -> str | None:
    """Return the note inside a list element."""
    try:
        return relation.span.text.lower().strip("()")
    except AttributeError:
        return None


async def generate_slug(name: str) -> str:
    """When brucebase_url is missing, make a fake url."""
    return slugify.slugify(name)


async def get_onstage(  # noqa: C901
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
                        "relation_id": "",
                        "band_id": "",
                        "note": await get_relation_note(link),
                    }

                    # fix for when there is no url associated with a link
                    try:
                        current["relation_id"] = await get_relation_id(m.a["href"])
                        current["band_id"] = await get_relation_id(link.a["href"])
                    except TypeError:
                        current["relation_id"] = await generate_slug(m.text.strip())
                        current["band_id"] = None

                    if current not in results["onstage"]:
                        results["onstage"].append(current)
            except AttributeError:
                current = {
                    "event_id": event_id["id"],
                    "relation_id": None,
                    "band_id": None,
                    "note": await get_relation_note(link),
                }

                # fix for when there is no url associated with a link
                try:
                    current["relation_id"] = await get_relation_id(link.a["href"])
                except TypeError:
                    current["relation_id"] = await generate_slug(link.text.strip())

                if current not in results["onstage"]:
                    results["onstage"].append(current)

    for item in results["onstage"]:
        item["relation_id"] = await get_relation_id(item["relation_id"], cur)
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
