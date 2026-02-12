"""Functions to get data and populate the database.

This module provides:
- get_event_details: Scrapes data from a provided event_url.
- basic_database: Populate the database with the basic amount of information.
"""

import datetime
import time

import httpx
import psycopg
from archive import get_list_from_archive
from covers import get_covers
from database import db
from event_page import scrape_event_page
from events import event_num_fix
from locations import update_locations
from relations import bands, relations
from setlist.setlist_stats import update_notes, update_setlist_stats
from songs import update_song_info
from tools.scraping import scraper
from tours import update_tour_counts, update_tour_legs, update_tour_runs, update_tours
from venues import update_venues

current_datetime = datetime.datetime.now(tz=datetime.UTC)


def get_new_setlists(
    cur: psycopg.Cursor,
    client: httpx.Client,
) -> None:
    """Check site for new setlists.

    Dates must be after the last item in SETLISTS, but before or equal to current date.
    """
    res = cur.execute(
        """SELECT brucebase_url FROM "events" WHERE event_id >
            (SELECT MAX(event_id) FROM "setlists") AND event_date <= now()
            AND NOT starts_with(brucebase_url, '/nogig:');""",
    )

    events_to_get = res.fetchall()

    if len(events_to_get) > 0:
        for row in events_to_get:
            scrape_event_page(row["brucebase_url"], cur, conn, client)


def update_get_new(
    cur: psycopg.Cursor,
    conn: psycopg.Connection,
    client: httpx.Client,
) -> None:
    """Pull new data from Brucebase and insert."""
    # get_songs(cur, client)
    # get_events(cur, conn, client)
    get_covers(cur, client)
    get_list_from_archive(cur, client)


def update_existing(cur: psycopg.Cursor, client: httpx.Client) -> None:
    """Update existing counts in database."""
    update_locations(cur)
    event_num_fix(cur)
    update_tours(cur)
    update_tour_runs(cur)
    update_tour_legs(cur)
    update_venues(cur)
    relations.update_relations(cur)
    bands.update_bands(cur)
    update_notes(cur)


def update_stats(cur: psycopg.Cursor) -> None:
    """Update various statistics."""
    update_song_info(cur)
    update_setlist_stats(cur)


def main(cur: psycopg.Cursor, conn: psycopg.Connection) -> None:
    """Test."""
    client = scraper.get_client()

    # update_get_new(cur, conn, client)
    # update_existing(cur, client)
    update_stats(cur)


if __name__ == "__main__":
    start = time.perf_counter()

    with db.load_db() as conn, conn.cursor() as cur:
        main(cur, conn)

    end = time.perf_counter()

    print(f"Time: {(end - start)} sec")
    print(f"End Time: {current_datetime.hour}:{current_datetime.minute}")
