"""Functions to get a list of people that have appeared with Bruce."""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


def update_relations(cur: psycopg.Cursor) -> None:
    """Get a list of all the people who have been on stage with Bruce."""
    try:
        cur.execute(
            """
            WITH onstage_stats AS (
                SELECT 
                    o.relation_id,
                    COUNT(distinct o.event_id) AS count,
                    (ARRAY_AGG(e.id ORDER BY e.event_id ASC))[1] AS first,
                    (ARRAY_AGG(e.id ORDER BY e.event_id DESC))[1] AS last
                FROM onstage o
                JOIN events e ON o.event_id = e.id
                GROUP BY o.relation_id
            )
            UPDATE relations r
            SET 
                appearances = os.count,
                first_event = os.first,
                last_event = os.last
            FROM onstage_stats os
            WHERE r.id = os.relation_id;
            """,
        )
    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Relations: Could not complete operation:", e)
    else:
        print("Got Relations")
