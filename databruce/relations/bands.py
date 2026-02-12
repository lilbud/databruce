"""Functions to handle the Relations list of Bands."""

import psycopg
from psycopg.rows import dict_row


def update_bands(cur: psycopg.Cursor) -> None:
    """Get a list of all the bands that Bruce has either played or recorded with."""
    try:
        cur.execute(
            """
            UPDATE bands SET num_events = 0, first_event = null, last_event = null;

            WITH band_stats AS (
                SELECT
                    o.band_id,
                    COUNT(distinct o.event_id) AS count,
                    (ARRAY_AGG(e.id ORDER BY e.event_id ASC))[1] AS first,
                    (ARRAY_AGG(e.id ORDER BY e.event_id DESC))[1] AS last
                FROM onstage o
                JOIN events e ON o.event_id = e.id
                GROUP BY 1
            )
            UPDATE bands r
            SET
                num_events = bs.count,
                first_event = bs.first,
                last_event = bs.last
            FROM band_stats bs
            WHERE r.id = bs.band_id;
            """,
        )
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Bands: Could not complete operation:", e)
    else:
        print("Got Bands")
