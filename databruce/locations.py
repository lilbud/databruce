"""Function for getting updated location info.

This module provides:
- update_locations: Update the various location tables, as well as their counts.
"""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def update_cities(cur: psycopg.AsyncCursor) -> None:
    """Update CITIES table with all cities listed in VENUES table."""
    try:
        await cur.execute(
            """
            UPDATE "cities"
            SET
                num_events = t.num,
                first_played = t.first,
                last_played = t.last
            FROM (
                SELECT
                    v.city,
                    SUM(v.num_events) AS num,
                    MIN(v.first_played) AS first,
                    MAX(v.last_played) AS last
                FROM venues v
                LEFT JOIN events e ON e.event_id = v.last_played
                WHERE e.event_date <= NOW()
                GROUP BY v.city
                ORDER BY v.city
            ) t
            WHERE "cities".id = t.city
            """,
        )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("CITIES: Could not complete operation:", e)


async def update_states(cur: psycopg.AsyncCursor) -> None:
    """Update STATES table with all states listed in VENUES table."""
    try:
        await cur.execute(
            """
            UPDATE "states"
            SET
                num_events = t.num,
                first_played = t.first,
                last_played = t.last
            FROM (
                SELECT
                    v.state,
                    SUM(v.num_events) AS num,
                    MIN(v.first_played) AS first,
                    MAX(v.last_played) AS last
                FROM venues v
                LEFT JOIN events e ON e.event_id = v.last_played
                WHERE e.event_date <= NOW()
                GROUP BY v.state
                ORDER BY v.state
            ) t
            WHERE "states".id = t.state
            """,
        )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)


async def update_countries(cur: psycopg.AsyncCursor) -> None:
    """Update COUNTRIES table with all countries listed in VENUES table."""
    try:
        await cur.execute(
            """
            UPDATE "countries"
            SET
                num_events = t.num,
                first_played = t.first,
                last_played = t.last
            FROM (
                SELECT
                    v.country,
                    SUM(v.num_events) AS num,
                    MIN(v.first_played) AS first,
                    MAX(v.last_played) AS last
                FROM venues v
                LEFT JOIN events e ON e.event_id = v.last_played
                WHERE e.event_date <= NOW()
                GROUP BY v.country
                ORDER BY v.country
            ) t
            WHERE "countries".id = t.country
            """,
        )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)


async def update_continents(cur: psycopg.AsyncCursor) -> None:
    """Update CONTINENTS table with all continents listed in VENUES table."""
    try:
        await cur.execute(
            """
            UPDATE "continents"
            SET
                num_events = t.num
            FROM (
                SELECT
                    continent,
                    SUM(num_events) AS num
                FROM venues
                WHERE continent IS NOT NULL
                GROUP BY continent
            ) t
            WHERE "continents".id = t.continent
            """,
        )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)


async def update_locations(pool: AsyncConnectionPool) -> None:
    """Update the various location tables, as well as their counts."""
    # get locations from VENUES
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await update_cities(cur)
        await update_states(cur)
        await update_countries(cur)
        await update_continents(cur)

    print("Updated Locations")
