import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def debut_premiere(pool: AsyncConnectionPool) -> None:
    """Mark song premieres and tour debuts."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE "setlists"
                SET
                    debut=true, premiere=false
                FROM (
                    SELECT
                            *
                    FROM "premiere_debut"
                ) t
                WHERE "setlists".setlist_song_id = ANY(t.debuts);

                UPDATE "setlists"
                SET
                    premiere=true, debut = false
                FROM (
                    SELECT
                            *
                    FROM "premiere_debut"
                ) t
                WHERE "setlists".setlist_song_id = t.premiere;
                """,
            )

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
