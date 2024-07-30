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
            LEFT JOIN "countries" c ON c.id = s.state_country
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
        res = await cur.execute(
            """SELECT country, sum(num_events) AS count FROM "venues"
                WHERE country IS NOT NULL
                GROUP BY country ORDER BY country""",
        )

        for row in await res.fetchall():
            await cur.execute(
                """INSERT INTO "countries" (name, num_events)
                    VALUES (%(name)s, %(num_events)s) ON CONFLICT(name)
                    DO UPDATE SET num_events=%(num_events)s""",
                {"name": row["country"], "num_events": row["count"]},
            )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
