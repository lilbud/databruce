import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def debut_premiere(pool: AsyncConnectionPool) -> None:
    """Mark song premieres and tour debuts."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE
                    "setlists"
                SET
                    debut = CASE
                        WHEN id = ANY (t.debuts) THEN true
                        ELSE FALSE
                    END,
                    premiere = CASE
                        WHEN id = t.premiere THEN TRUE
                        ELSE FALSE
                    END
                FROM
                (
                    SELECT
                        debuts,
                        premiere
                    FROM
                    premiere_debut
                ) t
                WHERE id = t.premiere OR id = ANY(t.debuts)
                """,
            )

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Got premiere/debut stats")
