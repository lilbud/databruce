"""Function to handle getting a list of songs Bruce/E Street has played live.

This module provides:
- get_cover_list: Get a list of cover songs and update SONGS table in db.
- songs_missing_url: Update SONGS table with songs from SETLISTS that are missing URLs.
- update_songs: Update SONGS with number of times played, as well as first/last performance.
- get_songs: Get a list of songs from the site and inserts into database.
"""  # noqa: E501

import psycopg
from bs4 import BeautifulSoup as bs4
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from tools.parsing import html_parser
from tools.scraping import scraper


async def song_opener_closer_count(pool: AsyncConnectionPool) -> None:
    """Count the number of times a song has opened/closed a show."""
    async with pool.connection() as conn, conn.cursor(
        row_factory=dict_row,
    ) as cur:
        try:
            await cur.execute(
                """UPDATE "songs"
                        SET
                            opener = t.opener_count,
                            closer = t.closer_count
                        FROM (
                            SELECT
                            s.song_id,
                            SUM(CASE WHEN s.position IN ('Show Opener')
                                THEN 1 ELSE 0 END) AS opener_count,
                            SUM(CASE WHEN s.position IN ('Show Closer')
                                THEN 1 ELSE 0 END) AS closer_count
                        FROM "setlists" s
                        LEFT JOIN "event_details" e USING (event_id)
                        WHERE e.setlist_certainty = 'Confirmed'
                        GROUP BY s.song_id
                        ORDER BY s.song_id
                    ) t
                    WHERE "songs"."brucebase_url" = t.song_id""",
            )

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)


async def update_song_info(pool: AsyncConnectionPool) -> None:
    """Update SONGS with number of times played, as well as num times opened/closed."""
    async with pool.connection() as conn, conn.cursor(
        row_factory=dict_row,
    ) as cur:
        try:
            await cur.execute(
                """
                    UPDATE "songs"
                    SET
                        first_played=t.first,
                        last_played=t.last,
                        num_plays_public=t.public_count,
                        num_plays_private=t.private_count
                    FROM (
                        WITH private_count AS (
                            SELECT
                            s.song_id,
                            SUM(
                                CASE
                                    WHEN s.set_name = ANY(ARRAY['Soundcheck', 'Recording', 'Rehearsal']) THEN 1
                                    ELSE 0
                                END
                            ) AS count
                            FROM "setlists" s
                            GROUP BY s.song_id
                        )
                        SELECT
                            s.song_id AS id,
                            MIN(s.event_id) AS first,
                            MAX(s.event_id) AS last,
                            SUM(
                                CASE
                                    WHEN s.set_name <> ALL(ARRAY['Soundcheck', 'Recording', 'Rehearsal']) THEN 1
                                    ELSE 0
                                END
                            ) AS public_count,
                            p.count AS private_count
                        FROM "setlists" s
                        LEFT JOIN "private_count" p ON p.song_id = s.song_id
                        WHERE s.set_name <> ALL(ARRAY['Soundcheck', 'Recording', 'Rehearsal'])
                        GROUP BY s.song_id, p.count
                        ORDER BY s.song_id
                    ) t
                    WHERE "songs"."brucebase_url" = t.id;""",  # noqa: E501
            )

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("songs: Could not complete operation:", e)


async def get_songs(pool: AsyncConnectionPool) -> None:
    """Get a list of songs from the site and inserts into database."""
    response = await scraper.post("18072044")

    # duplicate song ids which redirect
    ignore = [
        "born-in-the-usa",
        "land-of-1-000-dances",
        "deportee-plane-wreck-at-los-gatos",
    ]

    if response:
        soup = bs4(response, "lxml")

        songs = await html_parser.get_clean_links(soup, "/song:")

        links = [
            [link["url"], link["text"]] for link in songs if link["url"] not in ignore
        ]

    async with pool.connection() as conn, conn.cursor(
        row_factory=dict_row,
    ) as cur:
        try:
            await cur.executemany(
                """INSERT INTO "songs" (brucebase_url, song_name)
                        VALUES (%s, %s) ON CONFLICT(brucebase_url) DO NOTHING RETURNING *""",
                (links),
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
