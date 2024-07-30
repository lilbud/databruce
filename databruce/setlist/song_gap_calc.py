from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def calc_song_gap(pool: AsyncConnectionPool) -> None:
    """Calculate the number of events between songs being played."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
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
