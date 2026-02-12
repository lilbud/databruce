"""Function for getting updated location info.

This module provides:
- update_locations: Update the various location tables, as well as their counts.
"""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


def update_cities(cur: psycopg.Cursor) -> None:
    """Update CITIES table with all cities listed in VENUES table."""
    try:
        cur.execute(
            """
            WITH city_stats AS (
                SELECT 
                    c.id,
                    COUNT(distinct e.id) AS event_count,
                    (ARRAY_AGG(e.id ORDER BY e.event_id ASC) FILTER (WHERE e.id IS NOT NULL))[1] AS first,
                    (ARRAY_AGG(e.id ORDER BY e.event_id DESC) FILTER (WHERE e.id IS NOT NULL))[1] AS last
                FROM cities c
                left join venues v on v.city = c.id
                left join events e on e.venue_id = v.id
                GROUP BY 1
            )

            UPDATE cities c
            set
                num_events = cs.event_count,
                first_event = cs.first,
                last_event = cs.last
            from city_stats cs
            where c.id = cs.id
            """,
        )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("CITIES: Could not complete operation:", e)
    else:
        print("Updated CITIES with info from VENUES")


def update_states(cur: psycopg.Cursor) -> None:
    """Update STATES table with all states listed in VENUES table."""
    try:
        cur.execute(
            """
            WITH state_stats AS (
                SELECT
                    s.id,
                    COUNT(distinct e.id) AS event_count,
                    (ARRAY_AGG(e.id ORDER BY e.event_id ASC) FILTER (WHERE e.id IS NOT NULL))[1] AS first,
                    (ARRAY_AGG(e.id ORDER BY e.event_id DESC) FILTER (WHERE e.id IS NOT NULL))[1] AS last
                FROM states s
                left join cities c on c.state = s.id
                left join venues v on v.city = c.id
                left join events e on e.venue_id = v.id
                left join setlists s1 on s1.event_id = e.id
                GROUP BY 1
            )

            UPDATE states s
            set
                num_events = ss.event_count,
                first_event = ss.first,
                last_event = ss.last
            from state_stats ss
            where s.id = ss.id
            """,
        )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
    else:
        print("Updated STATES with info from VENUES")


def update_countries(cur: psycopg.Cursor) -> None:
    """Update COUNTRIES table with all countries listed in VENUES table."""
    try:
        cur.execute(
            """
            WITH country_stats AS (
            SELECT 
                c.id,
                COUNT(distinct e.id) AS event_count,
                (ARRAY_AGG(e.id ORDER BY e.event_id ASC) FILTER (WHERE e.id IS NOT NULL))[1] AS first,
                (ARRAY_AGG(e.id ORDER BY e.event_id DESC) FILTER (WHERE e.id IS NOT NULL))[1] AS last
            FROM countries c
            left join cities c1 on c1.country = c.id
            left join venues v on v.city = c1.id
            left join events e on e.venue_id = v.id
            GROUP BY 1
            )
            UPDATE countries c
            set
                num_events = cs.event_count,
                first_event = cs.first,
                last_event = cs.last
            from country_stats cs
            where c.id = cs.id
            """,
        )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
    else:
        print("Updated COUNTRIES with info from VENUES")


def update_continents(cur: psycopg.Cursor) -> None:
    """Update CONTINENTS table with all continents listed in VENUES table."""
    try:
        cur.execute(
            """
            update continents set num_events = 0;

            with continent_stats as (
                SELECT
                    c.id,
                    count(distinct e.event_id) as event_count
                FROM continents c
                left join countries c1 on c1.continent = c.id
                left join states s on s.country = c1.id
                left join cities c2 on c2.state = s.id
                left join venues v on v.city = c2.id
                left join events e on e.venue_id = v.id
                group by 1
            )

            UPDATE continents c
            SET
                num_events = cs.event_count
            FROM continent_stats cs
            WHERE c.id = cs.id
            """,
        )

    except (psycopg.OperationalError, psycopg.IntegrityError) as e:
        print("Could not complete operation:", e)
    else:
        print("Updated CONTINENTS with info from VENUES")


def update_locations(cur: psycopg.Cursor) -> None:
    """Update the various location tables, as well as their counts."""
    # get locations from VENUES
    update_cities(cur)
    update_states(cur)
    update_countries(cur)
    update_continents(cur)

    print("Updated Locations")
