import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def opener_closer(pool: AsyncConnectionPool) -> None:
    """Get song position in setlist and insert into SETLIST table."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE "setlists" SET position = NULL;
                UPDATE "setlists"
                    SET
                        position = t.position
                    FROM (
                        with "min_max" AS (
                        SELECT
                            s.event_id,
                            s.set_name,
                            s.song_id,
                            MIN(s.song_num::int) OVER
                                (PARTITION BY s.event_id, s.set_name) AS opener_id,
                            MAX(s.song_num::int) OVER
                                (PARTITION BY s.event_id, s.set_name) AS closer_id
                        FROM "setlists" s
                        )
                        SELECT
                            m.event_id,
                            (CASE
                                WHEN m.set_name = 'Set 1' THEN 'Show' ELSE m.set_name
                            END) || ' Opener' AS position,
                            MIN(m.opener_id) AS id
                        FROM "min_max" m
                        WHERE m.set_name = ANY(ARRAY['Show', 'Set 1', 'Set 2', 'Encore', 'Pre-Show', 'Post-Show'])
                        GROUP BY event_id, set_name HAVING COUNT(m.song_id) > 1
                        UNION ALL
                        SELECT
                            m.event_id,
                            (CASE
                                WHEN m.set_name = 'Show' THEN 'Main Set'
                                WHEN m.set_name = 'Encore' THEN 'Show'
                                ELSE m.set_name
                            END) || ' Closer' AS position,
                            MAX(m.closer_id) AS id
                        FROM "min_max" m
                        WHERE set_name = ANY(ARRAY['Show', 'Set 1', 'Set 2', 'Encore', 'Pre-Show', 'Post-Show'])
                        GROUP BY event_id, set_name HAVING COUNT(m.song_id) > 1
                        ORDER BY event_id, id ASC
                    ) t
                    WHERE "setlists"."song_num" = t.id AND
                        "setlists"."event_id" = t.event_id AND "setlists".position IS NULL""",  # noqa: E501
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Got opener/closer")
