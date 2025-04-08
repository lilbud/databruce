import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def calc_song_gap(pool: AsyncConnectionPool) -> None:
    """Calculate the number of events between songs being played."""
    async with pool.connection() as conn, conn.cursor() as cur:
        try:
            await cur.execute(
                """
                UPDATE "setlists" SET last=NULL, next=NULL, last_time_played=NULL;

                UPDATE "setlists"
                SET
                    last = t.last,
                    next = t.next,
                    last_time_played = t.last_time_played
                FROM (
                    SELECT * FROM "song_gaps" ORDER BY id
                ) t
                WHERE "setlists"."id" = t.id
                """,
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Got song gap stats")
