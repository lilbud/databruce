"""Tour related functions."""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def update_tour_runs(pool: AsyncConnectionPool) -> None:
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE "runs" SET first_event = NULL, last_event = NULL;

                UPDATE "runs"
                SET
                    first_event = t.first,
                    last_event = t.last,
                    num_shows = t.event_count,
                    num_songs = t.song_count
                FROM (
                    SELECT
                        e.run AS id,
                        MIN(e.event_id) AS first,
                        MAX(e.event_id) AS last,
                        COUNT(DISTINCT e.event_id) AS event_count,
                        COUNT(DISTINCT s.song_id) AS song_count
                    FROM events e
                    LEFT JOIN setlists s USING(event_id)
                    WHERE e.run IS NOT NULL
                    GROUP BY e.run
                ) t
                WHERE "runs"."id" = t.id
                """,
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("TOURS: Could not complete operation:", e)
        else:
            print("Updated TOUR_RUNS with info from EVENTS")


async def update_tours(pool: AsyncConnectionPool) -> None:
    """Get a list of tours from the EVENTS table."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE "tours" SET first_show=NULL, last_show=NULL;

                UPDATE "tours"
                    SET
                        first_show=t.first,
                        last_show=t.last,
                        num_songs=t.song_count,
                        num_shows=t.event_count,
                        num_legs=t.leg_count
                    FROM (
                        SELECT
                            e.tour_id,
                            MIN(s.event_id) AS first,
                            MAX(s.event_id) AS last,
                            COUNT(DISTINCT(s.song_id)) AS song_count,
                            COUNT(DISTINCT(e.event_id)) AS event_count,
                            COUNT(DISTINCT(e.tour_leg)) AS leg_count
                        FROM "events" e
                        LEFT JOIN "setlists" s USING(event_id)
                        WHERE e.event_type NOT SIMILAR TO 'Rescheduled_*'
                        AND s.set_name <> ANY(ARRAY['Soundcheck', 'Rehearsal'])
                        AND e.tour_id IS NOT NULL
                        GROUP BY e.tour_id
                    ) t
                    WHERE "tours"."id" = t.tour_id""",
            )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("TOURS: Could not complete operation:", e)

    print("Updated Tours")
