"""Functions to get data and populate the database.

This module provides:
- get_event_details: Scrapes data from a provided event_url.
- basic_database: Populate the database with the basic amount of information.
"""

import asyncio
import datetime
import time

from archive_org import get_list_from_archive
from covers import get_covers
from database import db
from event_page import scrape_event_page
from events import get_events
from locations import update_locations
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from relations import bands, relations
from setlist.opener_closer import opener_closer
from setlist.premiere_debut import debut_premiere
from setlist.song_gap_calc import calc_song_gap
from songs import (
    get_songs,
    update_song_info,
)
from tours import update_tour_runs, update_tours
from venues import get_venues, update_venue_count

current_datetime = datetime.datetime.now(tz=datetime.UTC)


async def get_new_setlists(pool: AsyncConnectionPool) -> None:
    """Check site for new setlists.

    Dates must be after the last item in SETLISTS, but before or equal to current date.
    """
    event_id = current_datetime.strftime("%Y%m%d-01")

    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        res = await cur.execute(
            """SELECT brucebase_url FROM "events" WHERE event_id >
                        (SELECT MAX(event_id) FROM "setlists") AND event_id <= %(event)s
                        AND NOT starts_with(brucebase_url, '/nogig:');
                            """,
            {"event": event_id},
        )

        events_to_get = await res.fetchall()

        if len(events_to_get) > 0:
            for row in events_to_get:
                await scrape_event_page(row["brucebase_url"], cur, conn)


async def update_get_new(pool: AsyncConnectionPool) -> None:
    """Pull new data from Brucebase and insert."""
    await get_songs(pool)
    # await get_venues(pool)
    await get_events(pool)
    await get_covers(pool)
    await get_list_from_archive(pool)


async def update_existing(pool: AsyncConnectionPool) -> None:
    """Update existing counts in database."""
    await update_locations(pool)
    await update_tours(pool)
    await update_tour_runs(pool)
    await get_new_setlists(pool)
    await update_venue_count(pool)
    await relations.update_relations(pool)
    await bands.update_bands(pool)


async def update_stats(pool: AsyncConnectionPool) -> None:
    """Update various statistics."""
    await debut_premiere(pool)
    await calc_song_gap(pool)
    await update_song_info(pool)
    # await opener_closer(pool)


async def main(pool: AsyncConnectionPool) -> None:
    """Test."""
    async with pool as pool:
        await update_get_new(pool)
        await update_existing(pool)
        await update_stats(pool)


if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main(db.pool), loop_factory=asyncio.SelectorEventLoop)

    end = time.perf_counter()

    print(f"Time: {(end - start)} sec")
    print(f"End Time: {current_datetime.hour}:{current_datetime.minute}")
