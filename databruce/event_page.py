"""Functions to handle the Event page.

This module provides:
- get_show_descriptor_from_title: Return the descriptor in the page title
- tabview_handler: Return the data in each tab of the tabview of an event page.
- get_event_data: Scrapes page and gets data
"""

import re

import psycopg
from bs4 import BeautifulSoup as bs4
from tabview import on_stage, setlist
from tags.tags import get_tags
from tools.parsing import html_parser
from tools.scraping import scraper

MAIN_URL = "http://brucebase.wikidot.com"


async def get_event_id(
    event_date: str,
    event_url: str,
    cur: psycopg.AsyncCursor,
) -> str:
    """Get event_id if url already in events, otherwise create id based on date."""
    res = await cur.execute(
        """SELECT event_id FROM "events" WHERE brucebase_url = %s""",
        (event_url,),
    )

    try:
        url_check = await res.fetchone()
        return url_check["event_id"]
    except IndexError:
        res = await cur.execute(
            """SELECT
                replace(event_date::text, '-', '') || '-' ||
                lpad((count(event_id)+1)::text, 2, '0') AS id
            FROM "events"
            WHERE event_date = %s
            GROUP BY event_date""",
            (event_date),
        )

        event = await res.fetchone()
        return event["id"]


async def certainty(
    event_date: str,
    event_id: str,
    venue_id: str,
    cur: psycopg.AsyncCursor,
) -> None:
    """Update event_certainty based on date and location."""
    if "-00" in event_date:
        event_certainty = "Uncertain Date"
    elif "unknown" in venue_id:
        event_certainty = "Uncertain Location"
    elif "-00" in event_date and "unknown" in venue_id:
        event_certainty = "Uncertain Date, Location"
    else:
        event_certainty = "Confirmed"

    await cur.execute(
        """UPDATE "event_details" SET event_certainty=%s WHERE event_id=%s""",
        (event_certainty, event_id),
    )


async def tabview_handler(soup: bs4, event_url: str, cur: psycopg.Cursor) -> None:
    """Return the data in each tab of the tabview of an event page."""
    content = soup.find("div", {"class": "yui-content"})
    nav = soup.find("ul", {"class": "yui-nav"})

    try:
        for index, tab in enumerate(nav.find_all("li")):
            tab_content = content.find("div", {"id": f"wiki-tab-0-{index}"})
            match tab.text.strip():
                case "On Stage" | "In Studio":
                    await on_stage.get_onstage(tab_content, event_url, cur)
                case "Setlist":
                    await setlist.get_setlist(tab_content, event_url, cur)
    except AttributeError:
        return


async def add_to_event_details(
    event_id: str,
    event_type: str,
    cur: psycopg.AsyncCursor,
) -> None:
    """Add event to event_details if not there."""
    await cur.execute(
        """INSERT INTO "event_details" (event_id, event_type) VALUES (%s, %s)
            ON CONFLICT(event_id) DO NOTHING""",
        (event_id, event_type),
    )


async def get_event_type(event_url: str) -> str:
    """Get event_type from event_url."""
    event_types = {
        "/gig:": "Concert",
        "/rehearsal:": "Rehearsal",
        "/interview:": "Interview",
        "/nogig:": "No Event",
        "/nobruce:": "No Bruce",
        "/recording:": "Recording",
    }

    return event_types.get(re.findall("(/.*:)", event_url)[0], "")


async def get_venue_id(venue_url: str, cur: psycopg.AsyncCursor) -> int:
    """Get ID by venue_url."""
    res = await cur.execute(
        """SELECT id FROM venues WHERE brucebase_url = %s""",
        (venue_url,),
    )

    try:
        venue = await res.fetchone()
        return venue["id"]
    except TypeError:
        return None


async def scrape_event_page(
    event_url: str,
    cur: psycopg.AsyncCursor,
    conn: psycopg.Connection,
    event_id: str = "",
) -> None:
    """Scrapes page and gets data, tabs are handled by other functions."""
    response = await scraper.get(f"http://brucebase.wikidot.com{event_url}")

    if response:
        soup = bs4(response.text, "lxml")
        page_title = await html_parser.get_page_title(soup)
        event_date = await html_parser.get_event_date(event_url)

        venue_url = await html_parser.get_venue_url(soup)
        venue_id = await get_venue_id(venue_url, cur)

        show = await html_parser.get_show_descriptor_from_title(page_title)

        if event_id == "":
            event_id = await get_event_id(
                event_date,
                event_url,
                cur,
            )

        event_type = await get_event_type(event_url)

        # add event to event_details
        await add_to_event_details(event_id, event_type, cur)

        # check for unknown date or unknown in venue_id
        await certainty(event_date, event_id, venue_url, cur)

        # handle page tags and insert into database
        await get_tags(soup, event_id, cur)

        # handle the different tabs on each page
        await tabview_handler(soup, event_url, cur)
        await conn.commit()

        try:
            await cur.execute(
                """UPDATE "events" SET venue_id=%s, early_late=%s WHERE event_id=%s""",
                (
                    venue_id,
                    show,
                    event_id,
                ),
            )

            await conn.commit()
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
