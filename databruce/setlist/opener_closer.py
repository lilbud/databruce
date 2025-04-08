import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def opener_closer(pool: AsyncConnectionPool) -> None:
    """Get song position in setlist and insert into SETLIST table."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE "setlists"
                SET
                    position = t.position
                FROM
                (
                with event_sets AS (
                    SELECT
                    s.event_id,
                    array_agg(DISTINCT s.set_name) as sets
                    FROM setlists s
                    GROUP BY s.event_id
                ),
                "min_max" AS (
                    SELECT
                    s.id,
                    s.event_id,
                    s.set_name,
                    MIN(s.id) OVER (PARTITION BY s.event_id, s.set_name) AS opener,
                    MAX(s.id) OVER (PARTITION BY s.event_id, s.set_name) AS closer
                    FROM
                    "setlists" s
                    WHERE s.set_name = ANY(ARRAY['Show', 'Set 1', 'Set 2', 'Encore', 'Pre-Show', 'Post-Show'])
                )
                SELECT
                    s.id,
                    s.event_id,
                    s.set_name,
                    CASE
                    WHEN s.id = m.opener AND s.set_name = ANY(ARRAY['Show', 'Set 1']) THEN 'Show Opener'
                    WHEN s.id = m.opener AND s.set_name <> ANY(ARRAY['Show', 'Set 1']) THEN s.set_name || ' Opener'
                    WHEN s.id = m.closer AND 'Encore' = ANY(e.sets) AND s.set_name = ANY(ARRAY['Show', 'Set 2']) THEN 'Main Set Closer'
                    WHEN s.id = m.closer AND s.song_num = MAX(s.song_num) OVER (PARTITION BY s.event_id) THEN 'Show Closer'
                    WHEN s.id = m.closer THEN s.set_name || ' Closer'
                    ELSE NULL
                    END as position
                FROM setlists s
                LEFT JOIN min_max m USING (id)
                LEFT JOIN event_sets e ON e.event_id = s.event_id
                ORDER BY s.event_id, s.song_num
                ) t
                WHERE "setlists"."id" = t.id""",  # noqa: E501
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Got opener/closer")
