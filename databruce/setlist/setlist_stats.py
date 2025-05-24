import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def opener_closer(pool: AsyncConnectionPool) -> None:
    """Get song position in setlist and insert into SETLIST table."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE "setlists" SET position = null;

                UPDATE "setlists"
                SET
                    position = t.position
                FROM
                (
                WITH valid_events AS (
                    SELECT event_id FROM setlists GROUP BY event_id HAVING count(song_id) > 1
                ),
                event_sets AS (
                    SELECT
                    s.event_id,
                    array_agg(DISTINCT s.set_name) as sets
                    FROM setlists s
                    GROUP BY s.event_id
                ),
                "min_max" AS (
                SELECT
                    event_id,
                set_name,
                (SELECT id from setlists where event_id = t.event_id and song_num = min(opener) LIMIT 1) as opener,
                (SELECT id from setlists where event_id = t.event_id and song_num = max(closer) LIMIT 1) as closer
                FROM (
                SELECT
                    s.event_id,
                    s.set_name,
                    MIN(s.song_num) OVER (PARTITION BY s.event_id, s.set_name ORDER BY s.song_num) as opener,
                    MAX(s.song_num) OVER (PARTITION BY s.event_id, s.set_name ORDER BY s.song_num) as closer
                FROM setlists s
                WHERE s.set_name = ANY(ARRAY['Show', 'Set 1', 'Set 2', 'Encore', 'Pre-Show', 'Post-Show'])
                ) t
                GROUP BY 1,2
                )
                select * from (
                    SELECT
                    s.id,
                    s.event_id,
                    s.set_name,
                    CASE
                        WHEN s.id = m.opener AND s.set_name = ANY(ARRAY['Show', 'Set 1']) THEN 'Show Opener'
                        WHEN s.id = m.opener AND s.set_name <> ANY(ARRAY['Show', 'Set 1']) THEN s.set_name || ' Opener'
                        WHEN s.id = m.closer AND 'Encore' = ANY(e.sets) AND s.set_name = ANY(ARRAY['Show', 'Set 2']) THEN 'Main Set Closer'
                        WHEN s.id = m.closer AND s.song_num = MAX(s.song_num) OVER (PARTITION BY s.event_id ORDER BY s.song_num) THEN 'Show Closer'
                        WHEN s.id = m.closer THEN s.set_name || ' Closer'
                    END as position
                    FROM setlists s
                    LEFT JOIN valid_events v USING(event_id)
                    LEFT JOIN min_max m USING(event_id)
                    LEFT JOIN event_sets e USING(event_id)
                    ORDER BY s.event_id, s.song_num
                ) where position is not null
                ) t
                WHERE "setlists"."id" = t.id
                """,  # noqa: E501
            )
            await conn.commit()
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Got opener/closer")


async def debut_premiere(pool: AsyncConnectionPool) -> None:
    """Mark song premieres and tour debuts."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE "setlists" SET debut = false, premiere=false;

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

            await conn.commit()

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Got premiere/debut stats")


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

            await conn.commit()
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Got song gap stats")
