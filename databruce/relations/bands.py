"""Functions to handle the Relations list of Bands."""

import psycopg
from psycopg.rows import dict_row


def update_bands(cur: psycopg.Cursor) -> None:
    """Get a list of all the bands that Bruce has either played or recorded with."""
    try:
        cur.execute(
            """
            UPDATE "bands" SET appearances = 0, first_appearance=null, last_appearance=null;

            UPDATE "bands"
            SET
                appearances = t.num,
                first_appearance=t.first,
                last_appearance=t.last
            FROM
            (
                SELECT
                    o.band_id AS artist,
                    MIN(o.event_id) AS first,
                    MAX(o.event_id) AS last,
                    count(distinct event_id) AS num
                FROM
                "onstage" o
                GROUP BY o.band_id
            ) t
            WHERE
            "bands".id = t.artist;
            """,  # noqa: E501
        )
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
    else:
        print("Got Bands")
