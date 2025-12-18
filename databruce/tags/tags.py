"""Function for comparing page tags to provided list.

This module provides:
- get_tags: Search through the event_page tags and find those that match provided list.
- weekday_from_date: Return day of week for the given date provided date is valid.
"""

import json
from pathlib import Path

import psycopg
from bs4 import BeautifulSoup as bs4

json_path = Path(Path(__file__).parent, "tags.json")

with Path.open(json_path) as tags_json:
    tags_dict = json.load(tags_json)
    releases = tags_dict["releases"]
    important_tags = tags_dict["important_tags"]
    tours = tags_dict["tours"]


def get_tour(tour_tag: str, cur: psycopg.Cursor) -> str:
    """Get the proper tour id for a given tag."""
    res = cur.execute(
        """SELECT id FROM tours WHERE brucebase_tag=%s;""",
        (tour_tag,),
    )

    tour = res.fetchone()
    return tour["id"]


def get_tags(
    soup: bs4,
    event_id: str,
    cur: psycopg.Cursor,
) -> None:
    """Search through the event_page tags and find those that match provided list.

    Insert those tags into the database for the given event_url.
    """
    tags = {
        "bootleg": False,
        "official": False,
        "tour": None,
        "other_tags": [],
    }

    page_tags = soup.find("div", {"class": "page-tags"})

    if page_tags:
        for i in page_tags.find_all("a"):
            if releases.get(f"{i.text}"):
                match i.text:
                    case "bootleg" | "sbd" | "iem" | "ald":
                        tags["bootleg"] = True
                    case "retail" | "livedl":
                        tags["official"] = True
            elif tours.get(f"{i.text}"):
                tags["tour"] = get_tour(i.text, cur)

            if i.text not in tags["other_tags"]:
                tags["other_tags"].append(i.text)

        try:
            cur.execute(
                """UPDATE "events" SET tour_id = %s, bootleg = %s,
                official = %s WHERE event_id = %s""",
                (
                    tags["tour"],
                    tags["bootleg"],
                    tags["official"],
                    event_id,
                ),
            )

            cur.execute(
                """INSERT INTO "tags" (event_id, tags) VALUES (%(event)s, %(tags)s)
                ON CONFLICT(event_id) DO UPDATE SET tags=%(tags)s""",
                {
                    "event": event_id,
                    "tags": ", ".join(sorted(tags["other_tags"])),
                },
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
