import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def opener_closer(pool: AsyncConnectionPool) -> None:
    """Get song position in setlist and insert into SETLIST table."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE setlists SET position = null;

                UPDATE setlists
                SET
                    position = t.position
                FROM (
                SELECT id, event_id, position FROM (
                SELECT
                    s.event_id,
                    s.set_name,
                    s.id,
                    CASE
                        WHEN set_name IN ('Show', 'Set 1') AND song_num = MIN(song_num) OVER (PARTITION BY event_id, set_name) THEN 'Show Opener'
                        WHEN set_name NOT IN ('Show', 'Set 1') AND song_num = MIN(song_num) OVER (PARTITION BY event_id, set_name) THEN set_name || ' Opener'
                        WHEN set_name NOT IN ('Show', 'Set 2', 'Encore') AND song_num = MAX(song_num) OVER (PARTITION BY event_id, set_name) THEN set_name || ' Closer'
                        WHEN set_name IN ('Show', 'Set 2') AND song_num = MAX(song_num) OVER (PARTITION BY event_id, set_name) AND event_id IN (SELECT distinct event_id FROM setlists WHERE set_name = 'Encore') THEN 'Main Set Closer'
                        WHEN song_num = MAX(song_num) OVER (PARTITION BY event_id) THEN 'Show Closer'
                        ELSE set_name
                    END AS position
                FROM
                    setlists s
                LEFT JOIN events e USING(event_id)
                LEFT JOIN bands b ON b.id = e.artist
                WHERE s.set_name IN ('Show', 'Set 1', 'Set 2', 'Encore', 'Pre-Show', 'Post-Show')
                AND e.setlist_certainty = 'Confirmed'
                AND s.event_id IN (SELECT event_id FROM setlists GROUP BY 1 HAVING COUNT(song_id) > 2)
                AND b.springsteen_band IS TRUE
                ORDER BY
                    s.event_id, s.song_num
                ) t WHERE t.position is not null
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


async def band_premiere(pool: AsyncConnectionPool) -> None:
    """Calculate the FTP for a song for each band that played it."""
    async with pool.connection() as conn, conn.cursor() as cur:
        try:
            await cur.execute(
                """
                UPDATE setlists SET band_premiere = false;

                UPDATE setlists SET band_premiere = true where id in (
                    SELECT
                        t.setlist_id as id
                    FROM (
                        SELECT
                        s.id as setlist_id,
                        s.song_id,
                        e.artist,
                        ROW_NUMBER() OVER (PARTITION BY e.artist, s.song_id ORDER BY e.event_id, s.id) AS rn
                        FROM setlists s
                        LEFT JOIN events e ON s.event_id = e.event_id
                        LEFT JOIN bands b ON b.id = e.artist
                        WHERE s.set_name IN ('Show', 'Set 1', 'Set 2', 'Encore') AND b.springsteen_band is true
                    ) t
                    WHERE t.rn = 1
                )
                """,
            )

            await conn.commit()
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Got band FTP")
