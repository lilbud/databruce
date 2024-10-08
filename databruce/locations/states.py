"""Database utilities and functions.

This module provides:
- get_states: Update STATES table with all states listed in VENUES table.
- update_states_count: Update num_events in STATES.
"""

import psycopg


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
