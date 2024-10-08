"""Database utilities and functions."""

import psycopg


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
        print("Could not complete operation:", e)
