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


async def update_song_info(pool: AsyncConnectionPool) -> None:
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


# async def song_snippet_count(pool: AsyncConnectionPool) -> None:
#     """Count the number of times a song has been played as a snippet."""
#     async with (
#         pool.connection() as conn,
#         conn.cursor(
#             row_factory=dict_row,
#         ) as cur,
#     ):
#         try:
#             await cur.execute(
#                 """
#                 UPDATE "songs"
#                 SET
#                     num_plays_snippet = t.count
#                 FROM (
#                     SELECT
#                         s.brucebase_url,
#                         count(s1.snippet_id) AS count
#                     FROM songs s
#                     LEFT JOIN snippets s1 ON s1.snippet_id = s.brucebase_url
#                     GROUP BY s.brucebase_url
#                 ) t
#                 WHERE "songs"."brucebase_url" = t.brucebase_url""",
#             )

#         except (psycopg.OperationalError, psycopg.IntegrityError) as e:
#             print("Could not complete operation:", e)


# async def song_opener_closer_count(pool: AsyncConnectionPool) -> None:
#     """Count the number of times a song has opened/closed a show."""
#     async with (
#         pool.connection() as conn,
#         conn.cursor(
#             row_factory=dict_row,
#         ) as cur,
#     ):
#         try:
#             await cur.execute(
#                 """UPDATE "songs"
#                         SET
#                             opener = t.opener_count,
#                             closer = t.closer_count
#                         FROM (
#                             SELECT
#                             s.song_id,
#                             SUM(CASE WHEN s.position = 'Show Opener'
#                                 THEN 1 ELSE 0 END) AS opener_count,
#                             SUM(CASE WHEN s.position = 'Show Closer'
#                                 THEN 1 ELSE 0 END) AS closer_count
#                         FROM "setlists" s
#                         LEFT JOIN "events" e USING (event_id)
#                         WHERE e.setlist_certainty = 'Confirmed'
#                         GROUP BY s.song_id
#                         ORDER BY s.song_id
#                     ) t
#                     WHERE "songs"."brucebase_url" = t.song_id""",
#             )

#         except (psycopg.OperationalError, psycopg.IntegrityError) as e:
#             print("Could not complete operation:", e)


# async def update_song_info(pool: AsyncConnectionPool) -> None:
#     """Update SONGS with number of times played, as well as num times opened/closed."""
#     async with (
#         pool.connection() as conn,
#         conn.cursor(
#             row_factory=dict_row,
#         ) as cur,
#     ):
#         try:
#             await cur.execute(
#                 """
#                     UPDATE "songs" SET first_played=NULL, last_played=NULL, num_plays_public=0, num_plays_private=0;

#                     UPDATE "songs"
#                     SET
#                         first_played=t.first,
#                         last_played=t.last,
#                         num_plays_public=t.public_count,
#                         num_plays_private=t.private_count
#                     FROM (
#                         WITH first_last AS (
#                             SELECT
#                                 s.song_id,
#                                 MIN(s.event_id) AS first,
#                                 MAX(s.event_id) AS last
#                             FROM setlists s
#                             WHERE s.set_name <> ALL(ARRAY['Soundcheck', 'Recording', 'Rehearsal', 'Interview'])
#                             GROUP BY s.song_id
#                         )
#                             SELECT
#                                 s.song_id AS id,
#                                 f.first,
#                                 f.last,
#                                 SUM (
#                                     CASE
#                                         WHEN s.set_name = ANY(ARRAY['Soundcheck', 'Recording', 'Rehearsal', 'Interview']) THEN 1 ELSE 0
#                                     END
#                                 ) AS private_count,
#                                 SUM (
#                                     CASE
#                                         WHEN s.set_name <> ALL(ARRAY['Soundcheck', 'Recording', 'Rehearsal', 'Interview']) THEN 1 ELSE 0
#                                     END
#                                 ) AS public_count
#                             FROM setlists s
#                             LEFT JOIN first_last f ON f.song_id = s.song_id
#                             GROUP BY s.song_id, f.first, f.last
#                             ORDER BY s.song_id
#                     ) t
#                     WHERE "songs"."brucebase_url" = t.id;""",
#             )

#         except (psycopg.OperationalError, psycopg.IntegrityError) as e:
#             print("songs: Could not complete operation:", e)


async def get_songs(pool: AsyncConnectionPool) -> None:
    """Get a list of songs from the site and inserts into database."""
    response = await scraper.post("18072044")

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
            await cur.executemany(
                """INSERT INTO "songs" (brucebase_url, song_name)
                    VALUES (%s, %s) ON CONFLICT(brucebase_url)
                    DO NOTHING RETURNING *""",
                (links),
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("SONGS: Could not complete operation:", e)
        else:
            print("Got Songs")
