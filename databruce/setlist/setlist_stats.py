import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


def update_setlist_stats(cur: psycopg.Cursor) -> None:
    try:
        res = cur.execute(
            """call refresh_setlist_stats()""",
        )

        print(res.fetchone())
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("SETLIST_STATS: Could not complete operation:", e)


def opener_closer(cur: psycopg.Cursor) -> None:
    """Get song position in setlist and insert into SETLIST table."""
    try:
        cur.execute(
            """
            select refresh_setlist_positions();
            """,
        )
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
    else:
        print("Got opener/closer")


def debut_premiere(cur: psycopg.Cursor) -> None:
    """Mark song premieres and tour debuts."""
    try:
        res = cur.execute(
            """
            SELECT refresh_setlist_debut_premiere();
            """,
        )

        print(res.fetchone())
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
    else:
        print("Got premiere/debut stats")


def calc_song_gap(cur: psycopg.Cursor) -> None:
    """Calculate the number of events between songs being played."""
    try:
        cur.execute(
            """
            select refresh_song_gaps();
            """,
        )
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
    else:
        print("Got song gap stats")


def band_premiere(cur: psycopg.Cursor) -> None:
    """Calculate the FTP for a song for each band that played it."""
    try:
        cur.execute(
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
                    ROW_NUMBER() OVER (PARTITION BY e.artist, s.song_id
                        ORDER BY e.event_id, s.id) AS rn
                    FROM setlists s
                    LEFT JOIN events e ON s.event_id = e.event_id
                    LEFT JOIN bands b ON b.id = e.artist
                    WHERE s.set_name IN ('Show', 'Set 1', 'Set 2', 'Encore')
                        AND b.springsteen_band is true
                ) t
                WHERE t.rn = 1
            )
            """,
        )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
    else:
        print("Got band FTP")


def update_notes(cur: psycopg.Cursor) -> None:
    try:
        cur.execute(
            """
            insert into
                notes (event_id, num, note, setlist_id)
            select
                event_id,
                num,
                note,
                id
            from setlist_notes sn
            on conflict (setlist_id, note) do nothing
            """,
        )
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
    else:
        print("Inserted notes")
