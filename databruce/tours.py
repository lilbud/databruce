"""Tour related functions."""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


def update_tour_legs(cur: psycopg.Cursor) -> None:
    """Update counts for tour legs."""
    try:
        cur.execute(
            """
            UPDATE "tour_legs" SET first_event = NULL, last_event = NULL, num_shows = 0, num_songs = 0;

            WITH tour_leg_stats AS (
                SELECT 
                    t.id,
                    COUNT(distinct e.id) AS event_count,
                    COUNT(DISTINCT(s.song_id)) FILTER (WHERE s.set_name <> ALL(ARRAY['Soundcheck', 'Rehearsal', 'Recording', 'Interview'])) AS song_count,
                    (ARRAY_AGG(e.id ORDER BY e.event_id ASC))[1] AS first,
                    (ARRAY_AGG(e.id ORDER BY e.event_id DESC))[1] AS last
                FROM tour_legs t
                left join events e on e.tour_leg = t.id
                left join setlists s on s.event_id = e.id
                GROUP BY 1
            )
            UPDATE tour_legs tl
            set
                num_shows = tls.event_count,
                num_songs = tls.song_count,
                first_event = tls.first,
                last_event = tls.last
                from tour_leg_stats tls
            where tl.id = tls.id
            """,  # noqa: E501
        )
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("TOURS: Could not complete operation:", e)
    else:
        print("Updated TOUR_LEGS with info from EVENTS")


def update_tour_runs(cur: psycopg.Cursor) -> None:
    """Update first/last event and event count for each run."""
    try:
        cur.execute(
            """
            UPDATE runs SET first_event = NULL, last_event=NULL, num_shows=0, num_songs=0;

            WITH run_stats AS (
                SELECT 
                    r.id,
                    COUNT(distinct e.id) AS event_count,
                    COUNT(DISTINCT(s.song_id)) FILTER (WHERE s.set_name <> ALL(ARRAY['Soundcheck', 'Rehearsal', 'Recording', 'Interview'])) AS song_count,
                    (ARRAY_AGG(e.id ORDER BY e.event_id ASC))[1] AS first,
                    (ARRAY_AGG(e.id ORDER BY e.event_id DESC))[1] AS last
                FROM runs r
                left join events e on e.run = r.id
                left join setlists s on s.event_id = e.id
                GROUP BY 1
            )
            UPDATE runs r
            set
                num_shows = rs.event_count,
                num_songs = rs.song_count,
                first_event = rs.first,
                last_event = rs.last
            from run_stats rs
            where r.id = rs.id
            """,
        )
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("RUNS: Could not complete operation:", e)
    else:
        print("Updated TOUR_RUNS with info from EVENTS")


def update_tours(cur: psycopg.Cursor) -> None:
    """Get a list of tours from the EVENTS table."""
    try:
        cur.execute(
            """
            UPDATE "tours" SET first_event=NULL, last_event=NULL, num_songs=0, num_shows=0, num_legs = 0;

            WITH tour_stats AS (
                SELECT 
                t.id,
                COUNT(DISTINCT(s.song_id)) FILTER (WHERE s.set_name <> ALL(ARRAY['Soundcheck', 'Rehearsal', 'Recording', 'Interview'])) AS song_count,
                COUNT(DISTINCT(e.event_id)) FILTER (WHERE e.public is true) AS event_count,
                COUNT(distinct t1.id) AS leg_count,
                (ARRAY_AGG(e.id ORDER BY e.event_id ASC))[1] AS first,
                (ARRAY_AGG(e.id ORDER BY e.event_id DESC))[1] AS last
                FROM tours t
                left JOIN events e ON e.tour_id = t.id
                left join setlists s on s.event_id = e.id
                left join tour_legs t1 ON t1.tour_id = t.id
                GROUP BY 1
            )

            UPDATE tours t
            SET 
                num_shows = ts.event_count,
                num_songs = ts.song_count,
                num_legs = ts.leg_count,
                first_event = ts.first,
                last_event = ts.last
            FROM tour_stats ts
            WHERE t.id = ts.id;
            """,  # noqa: E501
        )
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("TOURS: Could not complete operation:", e)

    print("Updated Tours")


def update_tour_counts(cur: psycopg.Cursor) -> None:
    """Get a list of tours from the EVENTS table."""
    try:
        cur.execute(
            """
            select refresh_setlist_tour_count();
            """,
        )
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("TOURS: Could not complete operation:", e)

    print("Updated Tour Counts")
