"""Database utilities and functions."""

import psycopg


async def update_cities(cur: psycopg.AsyncCursor) -> None:
    """Update CITIES table with all cities listed in VENUES table."""
    try:
        res = await cur.execute(
            """SELECT city, state, country, sum(num_events) AS count
                FROM "venues" WHERE city IS NOT NULL
                GROUP BY city, state, country ORDER BY city""",
        )

        for row in await res.fetchall():
            await cur.execute(
                """INSERT INTO "cities" (name, state, country, num_events)
                VALUES (%(name)s, %(state)s, %(country)s, %(num_events)s)
                ON CONFLICT(name, state) DO UPDATE
                SET num_events=%(num_events)s""",
                {
                    "name": row["city"],
                    "state": row["state"],
                    "country": row["country"],
                    "num_events": row["count"],
                },
            )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
