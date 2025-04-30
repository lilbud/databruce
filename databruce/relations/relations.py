"""Functions to get a list of people that have appeared with Bruce."""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def update_relations(pool: AsyncConnectionPool) -> None:
    """Get a list of all the people who have been on stage with Bruce."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE "relations" SET appearances = 0, first_appearance=null, last_appearance=null;

                UPDATE "relations"
                SET
                    appearances=t.num,
                    first_appearance=t.first,
                    last_appearance=t.last
                FROM (
                    SELECT
                    relation_id,
                    count(distinct event_id) AS num,
                    MIN(event_id) AS first,
                    MAX(event_id) AS last
                    FROM "onstage"
                        GROUP BY relation_id
                ) t
                WHERE "relations".id=t.relation_id;
                """,
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Got Relations")
