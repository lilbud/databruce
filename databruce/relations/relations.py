"""Functions to get a list of people that have appeared with Bruce."""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def update_relations(pool: AsyncConnectionPool) -> None:
    """Get a list of all the people who have been on stage with Bruce."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            res = await cur.execute(
                """SELECT
                        o.relation_id AS id,
                        count(DISTINCT(o.event_id)) AS count,
                        MIN(o.event_id) AS first,
                        MAX(o.event_id) AS last
                    FROM "onstage" o
                    WHERE o.relation_id != ''
                    GROUP BY o.relation_id""",
            )

            for row in await res.fetchall():
                await cur.execute(
                    """INSERT INTO "relations" (brucebase_url, appearances,
                    first_appearance, last_appearance) VALUES
                        (%(id)s, %(num_events)s, %(first)s, %(last)s)
                    ON CONFLICT (brucebase_url) DO UPDATE SET
                    appearances=%(num_events)s, first_appearance=%(first)s,
                    last_appearance=%(last)s""",
                    {
                        "id": row["id"],
                        "num_events": row["count"],
                        "first": row["first"],
                        "last": row["last"],
                    },
                )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
