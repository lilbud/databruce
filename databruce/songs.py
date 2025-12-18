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
from psycopg_pool import ConnectionPool
from tools.parsing import html_parser
from tools.scraping import scraper


def update_song_info(cur: psycopg.Cursor) -> None:
    """Update counts and stats for the songs listed in the setlist table."""
    try:
        cur.execute(
            """
            UPDATE "songs" SET first_played=null, last_played=null, num_plays_public=0, num_plays_private=0, num_plays_snippet = 0, opener = 0, closer = 0;

            UPDATE "songs"
            SET
                first_played = t.first_played,
                last_played = t.last_played,
                num_plays_public = t.public_count,
                num_plays_private = t.private_count,
                opener = t.opener_count,
                closer = t.closer_count,
                num_plays_snippet = t.snippet_count
            FROM (
                SELECT
                    s.id,
                    MIN(s1.event_id) FILTER (WHERE s1.set_name IN ('Show', 'Set 1', 'Set 2', 'Encore', 'Pre-Show', 'Post-Show')) AS first_played,
                    MAX(s1.event_id) FILTER (WHERE s1.set_name IN ('Show', 'Set 1', 'Set 2', 'Encore', 'Pre-Show', 'Post-Show')) AS last_played,
                    COUNT(distinct s1.id) FILTER (WHERE s1.song_id = s.id AND s1.set_name IN ('Show', 'Set 1', 'Set 2', 'Encore', 'Pre-Show', 'Post-Show')) as public_count,
                    COUNT(distinct s1.id) FILTER (WHERE s1.song_id = s.id AND s1.set_name NOT IN ('Show', 'Set 1', 'Set 2', 'Encore', 'Pre-Show', 'Post-Show')) as private_count,
                    COUNT(distinct s1.id) FILTER (WHERE s1.song_id = s.id AND s1.position = 'Show Opener' AND e.setlist_certainty = 'Confirmed') AS opener_count,
                    COUNT(distinct s1.id) FILTER (WHERE s1.song_id = s.id AND s1.position = 'Show Closer' AND e.setlist_certainty = 'Confirmed') AS closer_count,
                    COUNT(distinct sn.*) FILTER (WHERE sn.snippet_id = s.id) AS snippet_count
                FROM songs s
                LEFT JOIN setlists s1 ON s1.song_id = s.id
                LEFT JOIN snippets sn ON sn.snippet_id = s.id
                LEFT JOIN events e ON e.event_id = s1.event_id
                GROUP BY 1
                ORDER BY 1
            ) t
            WHERE "songs"."id" = t.id;""",  # noqa: E501
        )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
    else:
        print("Updated song info")


def get_songs(cur: psycopg.Cursor, client: httpx.Client) -> None:
    """Get a list of songs from the site and inserts into database."""
    response = scraper.post("18072044", client)

    # duplicate song ids which redirect
    ignore = [
        "/song:born-in-the-usa",
        "/song:land-of-1-000-dances",
        "/song:land-of-1000-dances",
        "/song:deportee-plane-wreck-at-los-gatos",
    ]

    if response:
        soup = bs4(response, "lxml")

        songs = html_parser.get_all_links(soup, "/song:")

        links = [
            [link["url"], link["text"]] for link in songs if link["url"] not in ignore
        ]

        try:
            res = cur.executemany(
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
