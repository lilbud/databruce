"""Tour related functions."""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def update_tours(pool: AsyncConnectionPool) -> None:
    """Get a list of tours from the EVENTS table."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """UPDATE "tours"
                    SET
                        first_show=t.first,
                        last_show=t.last,
                        num_songs=t.song_count,
                        num_shows=t.event_count
                    FROM (
                        SELECT
                            e.tour,
                            MIN(e.event_id) AS first,
                            MAX(e.event_id) AS last,
                            COUNT(DISTINCT(s.song_id)) AS song_count,
                            COUNT(DISTINCT(e.event_id)) AS event_count
                        FROM "event_details" e
                        LEFT JOIN "setlists" s USING(event_id)
                        WHERE e.event_type NOT SIMILAR TO 'Rescheduled_*'
                        AND s.set_name <> ANY(ARRAY['Soundcheck', 'Rehearsal'])
                        AND e.tour IS NOT NULL
                        GROUP BY e.tour
                    ) t
                    WHERE "tours"."brucebase_id" = t.tour""",
            )

            # rehearsals specific
            await cur.execute(
                """UPDATE "tours"
                    SET
                        first_show=t.first,
                        last_show=t.last,
                        num_songs=t.song_count,
                        num_shows=t.event_count
                    FROM (
                        SELECT
                            e.tour,
                            MIN(e.event_id) AS first,
                            MAX(e.event_id) AS last,
                            COUNT(DISTINCT(s.song_id)) AS song_count,
                            COUNT(DISTINCT(e.event_id)) AS event_count
                        FROM "event_details" e
                        LEFT JOIN "setlists" s USING(event_id)
                        WHERE e.tour = 'tour_rehearsal'
                        GROUP BY e.tour
                    ) t
                    WHERE "tours"."brucebase_id" = t.tour""",
            )

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("TOURS: Could not complete operation:", e)
