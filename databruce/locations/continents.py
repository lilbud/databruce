"""Database utilities and functions.

This module provides:
- get_countries: Update COUNTRIES table with all countries listed in VENUES table.
- update_countries_count: Update num_events in COUNTRIES.
"""

import psycopg


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
