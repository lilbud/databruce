"""Database utilities and functions.

This module provides:
- get_countries: Update COUNTRIES table with all countries listed in VENUES table.
- update_countries_count: Update num_events in COUNTRIES.
"""

import psycopg


async def get_country_from_abbrev(state_abbrev: str, cur: psycopg.AsyncCursor) -> str:
    """Return the name of a country from the given state abbreviation."""
    try:
        res = await cur.execute(
            """SELECT
                c.name
            FROM "states" s
            LEFT JOIN "countries" c ON c.id = s.country
            WHERE s.state_abbrev=%s;""",
            (state_abbrev,),
        )

        name = await res.fetchone()

        return name["name"]
    except (KeyError, TypeError):
        return ""


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
