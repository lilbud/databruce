"""Functions to handle the Relations list of Bands."""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def update_bands(pool: AsyncConnectionPool) -> None:
    """Get a list of all the bands that Bruce has either played or recorded with."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            res = await cur.execute(
                """SELECT
                        o.band_id AS id,
                        count(DISTINCT(o.event_id)) AS count,
                        MIN(o.event_id) AS first,
                        MAX(o.event_id) AS last
                    FROM "onstage" o
                    WHERE o.band_id != ''
                    GROUP BY o.band_id""",
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            for row in await res.fetchall():
                await cur.execute(
                    """INSERT INTO "bands" (brucebase_url, appearances,
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
