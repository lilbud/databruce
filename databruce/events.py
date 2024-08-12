"""Functions to handle getting events from Brucebase.

This module provides:
- event_url_check: Check database for duplicate event URLs.
- get_events: Get events from the site and inserts them into the database.
"""

import re

import httpx
import psycopg
from bs4 import BeautifulSoup as bs4
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from tools.parsing import html_parser
from tools.scraping import scraper

# only gets URLs matching one of the event page types,
# and that the year is only from 1965 ->
# which is when Bruce starts playing live

URL_MATCH_PATTERN = (
    r"\/(gig|nogig|interview|rehearsal|nobruce|recording):(?!(19(49|5\d|6[0-4]))).*$"
)


async def get_event_id(event_date: str, cur: psycopg.AsyncCursor) -> str:
    """Get the number of event_ids for a date, then append 1 if exists already."""
    event_id = re.sub("-", "", event_date)

    res = await cur.execute(
        """SELECT count(event_id) AS id FROM "events" WHERE event_id LIKE %s""",
        (f"{event_id}%",),
    )

    max_date = await res.fetchone()

    if max_date["id"] > 1:
        return f"{event_id}-{str(int(max_date["id"])+1).zfill(2)}"

    return f"{event_id}-01"


async def get_events_from_db(cur: psycopg.AsyncCursor) -> list["str"]:
    """Get a list of event_urls from database."""
    res = await cur.execute(
        """SELECT brucebase_url FROM "events" ORDER BY event_id;""",
    )

    return [row["brucebase_url"] for row in await res.fetchall()]


async def get_events(pool: AsyncConnectionPool) -> None:
    """Get events from Brucebase."""
    links = []

    event_cat = {
        "gig": "17778567",
        "interview": "18227972",
        "nobruce": "33229034",
        "nogig": "17786098",
        "recording": "19114187",
        "rehearsal": "18433049",
    }

    ignore = [
        "/gig:1999-07-18-caa-east-rutherford-nj-2",
        "/gig:2000-07-01-madison-square-garden-new-york-city-ny-2",
        "/gig:2009-06-05-stockholms-stadion-stockholm-sweden-2",
        "/gig:2012-07-31-olympiastadion-helsinki-finland-2",
        "/recording:1985-01-28-a-m-studios-hollywood-ca-2",
        "/recording:1985-07-00-shakedown-studios-new-york-city-ny-3",
        "/recording:1985-07-00-shakedown-studios-new-york-city-ny-2",
        "/recording:1986-02-00-shorefire-studios-long-branch-nj-2",
        "/recording:1987-02-00-shakedown-studios-new-york-city-ny-2",
    ]
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        db_events = await get_events_from_db(cur)

        async with httpx.AsyncClient() as client:
            for category_id in event_cat.values():
                response = await client.post(
                    "http://brucebase.wikidot.com/ajax-module-connector.php",
                    headers={
                        "User-Agent": await scraper.get_random_user_agent(),
                        "Cookie": "wikidot_token7=0",
                    },
                    data={
                        "category_id": category_id,
                        "moduleName": "list/WikiCategoriesPageListModule",
                        "wikidot_token7": "0",
                    },
                )

                if response:
                    soup = bs4(response.json()["body"], "lxml")
                    urls = await html_parser.get_all_links(soup, URL_MATCH_PATTERN)

                    for url in urls:
                        if url["url"] not in db_events and url["url"] not in ignore:
                            print(url["url"])
                            links.append(url["url"])

        if len(links) > 0:
            for event_url in links:
                event_date = await html_parser.get_event_date(event_url)
                event_id = await get_event_id(event_date, cur)

                try:
                    await cur.execute(
                        """INSERT INTO "events"
                            (event_id, event_date, brucebase_url)
                            VALUES (%s, %s, %s) ON CONFLICT
                            (event_id, event_date, brucebase_url)
                            DO NOTHING RETURNING *""",
                        (event_id, event_date, event_url),
                    )
                except (psycopg.OperationalError, psycopg.IntegrityError) as e:
                    print("Could not complete operation:", e)
        else:
            print("No new events to add")
