"""Functions to handle the Event page.

This module provides:
- get_show_descriptor_from_title: Return the descriptor in the page title
- tabview_handler: Return the data in each tab of the tabview of an event page.
- get_event_data: Scrapes page and gets data
"""

import re

import httpx
import psycopg
from bs4 import BeautifulSoup as bs4
from events import get_event_id
from tabview import on_stage, setlist
from tags.tags import get_tags
from tools.parsing import html_parser
from tools.scraping import scraper
from venues import venue_parser

MAIN_URL = "http://brucebase.wikidot.com"


def tabview_handler(
    soup: bs4,
    event_id: str,
    event_url: str,
    cur: psycopg.Cursor,
) -> None:
    """Return the data in each tab of the tabview of an event page."""
    content = soup.find("div", {"class": "yui-content"})
    nav = soup.find("ul", {"class": "yui-nav"})

    try:
        for index, tab in enumerate(nav.find_all("li")):
            tab_content = content.find("div", {"id": f"wiki-tab-0-{index}"})

            match tab.text.strip():
                case "On Stage" | "In Studio" | "On Set":
                    on_stage.get_onstage(tab_content, event_id, cur)
                case "Setlist":
                    setlist.get_setlist(
                        tab_content,
                        event_id,
                        event_url,
                        cur,
                    )
    except AttributeError:
        return


def get_event_type(event_url: str) -> str | None:
    """Get event_type from event_url."""
    event_types = {
        "/gig:": "Concert",
        "/rehearsal:": "Rehearsal",
        "/interview:": "Interview",
        "/nogig:": "No Event",
        "/nobruce:": "No Bruce",
        "/recording:": "Recording",
    }

    return event_types.get(re.findall("(/.*:)", event_url)[0], None)


def get_venue_id(url: str, cur: psycopg.Cursor) -> int | None:
    """Get ID by venue_url."""
    res = cur.execute(
        """SELECT id FROM venues WHERE brucebase_url = %s""",
        (url,),
    )

    venue = res.fetchone()
    return venue["id"]


def scrape_event_page(
    event_url: str,
    cur: psycopg.Cursor,
    conn: psycopg.Connection,
    client: httpx.Client,
    event_id: str = "",
) -> None:
    """Scrapes page and gets data, tabs are handled by other functions."""
    response = scraper.get(f"http://brucebase.wikidot.com{event_url}", client)

    if response:
        soup = bs4(response.text, "lxml")
        page_title = html_parser.get_page_title(soup)
        event_date = html_parser.get_event_date(event_url)

        venue_url = html_parser.get_venue_url(soup)
        venue_id = get_venue_id(url=venue_url, cur=cur)
        show = html_parser.get_show_descriptor_from_title(page_title)

        # if event not provided, either get from database or generate new one
        if event_id == "":
            event_id = get_event_id(
                event_date,
                event_url,
                cur,
            )

        # get event type from url
        event_type = get_event_type(event_url)

        # handle page tags and insert into database
        get_tags(soup, event_id, cur)

        # handle the different tabs on each page
        tabview_handler(soup, event_id, event_url, cur)

        try:
            cur.execute(
                """UPDATE "events" SET venue_id=%(venue)s, early_late=%(early)s,
                        event_type=%(type)s WHERE event_id=%(event)s""",
                {
                    "venue": venue_id,
                    "early": show,
                    "type": event_type,
                    "event": event_id,
                },
            )

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            conn.commit()
