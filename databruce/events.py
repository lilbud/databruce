"""Functions to handle getting events from Brucebase.

This module provides:
- event_url_check: Check database for duplicate event URLs.
- get_events: Get events from the site and inserts them into the database.
"""

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
    res = await cur.execute(
        """SELECT max(event_id) AS id FROM "events" WHERE event_date = %s""",
        (f"{event_date}%",),
    )

    max_date = await res.fetchone()

    try:
        # get the last digit of the highest event id for a date
        # then append 1 to it and return
        last_num = str(int(max_date["id"][-1]) + 1).zfill(2)
        return f"{event_date.replace("-", "")}-{last_num}"
    except TypeError:
        return f"{event_date.replace("-", "")}-01"


async def get_events_from_db(cur: psycopg.AsyncCursor) -> list["str"]:
    """Get a list of event_urls from database."""
    res = await cur.execute(
        """SELECT brucebase_url FROM "events" ORDER BY event_id;""",
    )

    return [row["brucebase_url"] for row in await res.fetchall()]


async def event_num_fix(cur: psycopg.AsyncCursor) -> None:
    """Update event_num after new events inserted."""
    await cur.execute(
        """
        UPDATE "events" SET event_num = NULL;

        UPDATE "events"
        SET
            event_num=t.num
        FROM (
            SELECT
                row_number() OVER (ORDER BY event_id) AS num,
                event_id
            FROM "events"
        WHERE brucebase_url NOT LIKE '/nogig:%'
        ) t
        WHERE "events".event_id=t.event_id;
        """,
    )


async def get_events(pool: AsyncConnectionPool) -> None:
    """Get events from Brucebase."""
    event_cat = {
        "gig": "17778567",
        "interview": "18227972",
        "nobruce": "33229034",
        "nogig": "17786098",
        "recording": "19114187",
        "rehearsal": "18433049",
    }

    # weird events which redirect to an existing event url
    # I probably could just check before inserting, but
    # it would mean having to ping each page and on a massive
    # update it would take too long.
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
        "/gig:1984-08-20-brendan-byrne-arena-east-rutherford-nj-2",
    ]

    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        event_urls = await get_events_from_db(cur)

        for category_id in event_cat.values():
            response = await scraper.post(category_id)

            if response:
                soup = bs4(response, "lxml")
                urls = await html_parser.get_all_links(soup, URL_MATCH_PATTERN)

                for url in urls:
                    if url["url"] not in ignore and url["url"] not in event_urls:
                        event_url = url["url"]
                        event_date = await html_parser.get_event_date(event_url)
                        event_note = None

                        if "-00" in event_date:
                            event_note = "Placeholder date, actual date unknown."

                        event_id = await get_event_id(event_date, cur)

                        try:
                            await cur.execute(
                                """INSERT INTO "events" (event_id, event_date,
                                        brucebase_url, event_date_note)
                                    VALUES (%s, %s, %s, %s) ON CONFLICT
                                    (event_id, event_date, brucebase_url) DO NOTHING
                                    RETURNING *""",
                                (event_id, event_date, event_url, event_note),
                            )
                        except (
                            psycopg.OperationalError,
                            psycopg.IntegrityError,
                        ) as e:
                            print("EVENTS: Could not complete operation:", e)

        # fix event numbers after insert
        await event_num_fix(cur)
        print("Got Events")
