"""Functions to handle the Relations list of Bands."""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def update_bands(pool: AsyncConnectionPool) -> None:
    """Get a list of all the bands that Bruce has either played or recorded with."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE "bands" SET appearances = 0;

                UPDATE "bands"
                SET
                    appearances=t.num
                FROM (
                    SELECT
                        artist,
                    count(distinct event_id) AS num
                    FROM "events"
                GROUP BY artist
                ) t
                WHERE "bands".id=t.artist;
                """,
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Got Bands")
