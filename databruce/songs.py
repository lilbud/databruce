"""Function to handle getting a list of songs Bruce/E Street has played live.

This module provides:
- get_cover_list: Get a list of cover songs and update SONGS table in db.
- songs_missing_url: Update SONGS table with songs from SETLISTS that are missing URLs.
- update_songs: Update SONGS with number of times played, as well as first/last performance.
- get_songs: Get a list of songs from the site and inserts into database.
"""  # noqa: E501

import httpx
import psycopg
from bs4 import BeautifulSoup as bs4
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from tools.parsing import html_parser
from tools.scraping import scraper


async def update_song_info(pool: AsyncConnectionPool) -> None:
    """Update counts and stats for the songs listed in the setlist table."""
    async with pool.connection() as conn, conn.cursor() as cur:
        try:
            await cur.execute(
                """
                UPDATE "songs"
                SET
                    first_played = t.first,
                    last_played = t.last,
                    num_plays_public = t.public_count,
                    num_plays_private = t.private_count,
                    num_plays_snippet = t.snippet_count,
                    opener = t.opener_count,
                    closer = t.closer_count
                FROM (
                    SELECT
                        s.id,
                        s.brucebase_url,
                        MIN(s1.event_id) FILTER (WHERE s1.set_name <> ALL(ARRAY['Soundcheck', 'Recording', 'Rehearsal', 'Interview'])) AS first,
                        MAX(s1.event_id) FILTER (WHERE s1.set_name <> ALL(ARRAY['Soundcheck', 'Recording', 'Rehearsal', 'Interview'])) AS last,
                        COUNT(distinct s1.id) FILTER(WHERE s1.set_name <> ALL(ARRAY['Soundcheck', 'Recording', 'Rehearsal', 'Interview'])) AS public_count,
                        COUNT(distinct s1.id) FILTER(WHERE s1.set_name = ANY(ARRAY['Soundcheck', 'Recording', 'Rehearsal', 'Interview'])) AS private_count,
                        COUNT(distinct s2.event_id) AS snippet_count,
                        COUNT(*) FILTER (WHERE s1.position = 'Show Opener' AND e.setlist_certainty = 'Confirmed') AS opener_count,
                        COUNT(*) FILTER (WHERE s1.position = 'Show Closer' AND e.setlist_certainty = 'Confirmed') AS closer_count
                    FROM songs s
                    LEFT JOIN setlists s1 ON s1.song_id = s.id
                    LEFT JOIN snippets s2 ON s2.snippet_id = s.id
                    LEFT JOIN events e ON e.event_id = s1.event_id
                    GROUP BY s.id
                ) t
                WHERE "songs"."id" = t.id;""",  # noqa: E501
            )

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Updated song info")


async def get_songs(pool: AsyncConnectionPool, client: httpx.AsyncClient) -> None:
    """Get a list of songs from the site and inserts into database."""
    response = await scraper.post("18072044", client)

    # duplicate song ids which redirect
    ignore = [
        "/song:born-in-the-usa",
        "/song:land-of-1-000-dances",
        "/song:land-of-1000-dances",
        "/song:deportee-plane-wreck-at-los-gatos",
    ]

    if response:
        soup = bs4(response, "lxml")

        songs = await html_parser.get_all_links(soup, "/song:")

        links = [
            [link["url"], link["text"]] for link in songs if link["url"] not in ignore
        ]

    async with (
        pool.connection() as conn,
        conn.cursor(
            row_factory=dict_row,
        ) as cur,
    ):
        try:
            res = await cur.executemany(
                """INSERT INTO "songs" (brucebase_url, song_name)
                    VALUES (%s, %s) ON CONFLICT(brucebase_url)
                    DO NOTHING RETURNING *""",
                (links),
            )

            print(res)
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("SONGS: Could not complete operation:", e)
        else:
            print("Got Songs")
