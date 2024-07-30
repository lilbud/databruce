"""Database utilities and functions.

This module provides:
- get_states: Update STATES table with all states listed in VENUES table.
- update_states_count: Update num_events in STATES.
"""

import psycopg


async def update_states(cur: psycopg.AsyncCursor) -> None:
    """Update STATES table with all states listed in VENUES table."""
    try:
        res = await cur.execute(
            """SELECT
                    upper(v.state) AS state,
                    c.id AS country,
                    sum(v.num_events) AS count
                FROM "venues" v
                LEFT JOIN "countries" c ON c.name = v.country
                WHERE v.state != '' AND length(v.state) = 2
                GROUP BY v.state, c.id
                ORDER BY v.state""",
        )

        for row in await res.fetchall():
            await cur.execute(
                """INSERT INTO "states"
                    (state_abbrev, state_country, num_events) VALUES
                    (%(state)s, %(country)s, %(num_events)s) ON CONFLICT(state_abbrev)
                    DO UPDATE SET num_events=%(num_events)s""",
                {
                    "state": row["state"],
                    "country": row["country"],
                    "num_events": row["count"],
                },
            )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
