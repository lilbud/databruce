"""Functions to handle getting events from Brucebase.

This module provides:
- event_url_check: Check database for duplicate event URLs.
- get_events: Get events from the site and inserts them into the database.
"""

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


async def sessions(pool: AsyncConnectionPool) -> None:
    """Update counts for album sessions."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE "sessions" SET first_event = NULL, last_event = NULL, num_events=0, num_songs=0;

                UPDATE "sessions"
                SET
                    first_event = t.first,
                    last_event = t.last,
                    num_events = t.event_count,
                    num_songs = t.song_count
                FROM (
                    SELECT
                        e.session_id AS id,
                        MIN(e.event_id) AS first,
                        MAX(e.event_id) AS last,
                        COUNT(DISTINCT e.event_id) AS event_count,
                        COUNT(DISTINCT s.song_id) AS song_count
                    FROM events e
                    LEFT JOIN setlists s USING(event_id)
                    WHERE e.session_id IS NOT NULL
                    GROUP BY e.session_id
                ) t
                WHERE "sessions"."id" = t.id
                """,  # noqa: E501
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("SESSIONS: Could not complete operation:", e)
        else:
            print("Updated SESSIONS with info from EVENTS")


async def certainty(pool: AsyncConnectionPool) -> None:
    """Set event/setlist certainty.

    Event certainty is based on the date/venue. Empty date and/or venue with 'unknown'
    in the name is an Uncertain event.

    Setlist certainty is based on number of songs and if there is a bootleg at all.
    """
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            UPDATE events SET event_certainty=NULL, setlist_certainty=NULL;

            UPDATE events SET
                event_certainty = t.event,
                setlist_certainty = t.setlist
            FROM (
            SELECT
                e.event_id,
                CASE
                WHEN count(s.song_id) > 0 AND count(b.id) > 0 THEN 'Confirmed'
                WHEN count(s.song_id) > 0 AND count(b.id) = 0 THEN 'Probable'
                ELSE 'Unknown' END as setlist,
                CASE
                WHEN e.event_date IS NULL THEN 'Unknown Date'
                WHEN e.venue_id IS NULL THEN 'Unknown Location'
                WHEN e.event_date IS NULL AND v.name LIKE '%Unknown%' THEN 'Uncertain Date/Location'
                ELSE 'Confirmed'
                END as event
            FROM events e
            LEFT JOIN setlists s ON s.event_id = e.event_id
            LEFT JOIN bootlegs b ON b.event_id = e.event_id
            LEFT JOIN venues v ON v.id = e.venue_id
            GROUP BY e.event_id, v.name
            ) t
            WHERE "events"."event_id" = t.event_id
            """,
        )


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

    url_check = await res.fetchone()

    try:
        return url_check["event_id"]
    except TypeError:
        date = event_date.replace("-", "")

        res = await cur.execute(
            """SELECT
                CASE WHEN count(event_id)::int = 0 THEN 1 ELSE count(event_id) END as num
            FROM "events"
            WHERE event_id LIKE %s
            """,
            (f"{date}%",),
        )

        event_count = await res.fetchone()

        return f"{date}-{str(event_count['num'] + 1).zfill(2)}"


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


async def get_events(pool: AsyncConnectionPool, client: httpx.AsyncClient) -> None:
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
            response = await scraper.post(category_id, client)

            if response:
                soup = bs4(response, "lxml")
                urls = await html_parser.get_all_links(soup, URL_MATCH_PATTERN)

                for url in urls:
                    if url["url"] not in ignore and url["url"] not in event_urls:
                        event_url = url["url"]

                        event_date = await html_parser.get_event_date(event_url)
                        event_id = await get_event_id(event_date, event_url, cur)
                        event_note = None

                        if "-00" in event_date:
                            event_note = "Placeholder date, actual date unknown."
                            event_date = None

                        try:
                            await cur.execute(
                                """INSERT INTO "events" (event_id, event_date,
                                        brucebase_url, event_date_note)
                                    VALUES (%s, %s, %s, %s) ON CONFLICT
                                    (event_id, event_date, brucebase_url) DO NOTHING
                                    RETURNING *""",
                                (event_id, event_date, event_url, event_note),
                            )

                            await conn.commit()
                        except (
                            psycopg.OperationalError,
                            psycopg.IntegrityError,
                        ) as e:
                            print("EVENTS: Could not complete operation:", e)

        # fix event numbers after insert
        await event_num_fix(cur)
        print("Got Events")
