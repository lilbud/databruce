"""Functions for getting a list of venues from Brucebase.

This module provides:
- venue_name_fix: Fix venue names which are formatted incorrectly on the site.
- venue_parser: Parse venue name and return list of its components.
- get_venues: Get a list of venues from Brucebase, and inserts into the database.
- update_venue_info: Update EVENTS with venue info. Update VENUES with event count.
"""

import re

import ftfy
import psycopg
from bs4 import BeautifulSoup as bs4
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from tools.parsing import html_parser
from tools.scraping import scraper


async def get_country_from_abbrev(state_abbrev: str, cur: psycopg.AsyncCursor) -> str:
    """Return the name of a country from the given state abbreviation."""
    try:
        res = await cur.execute(
            """SELECT
                c.name
            FROM "states" s
            LEFT JOIN "countries" c ON c.id = s.country
            WHERE s.state_abbrev=%s;""",
            (state_abbrev,),
        )

        name = await res.fetchone()

        return name["name"]
    except (KeyError, TypeError):
        return ""


async def get_city_id(city_name: str, cur: psycopg.AsyncCursor) -> int:
    """Get id based on city name."""
    res = await cur.execute(
        """SELECT id FROM cities WHERE name = %s""",
        (city_name,),
    )

    try:
        city = await res.fetchone()
        return city["id"]
    except TypeError:
        return None


async def get_state_id(state: str, cur: psycopg.AsyncCursor) -> int:
    """Get id based on state."""
    res = await cur.execute(
        """SELECT id FROM states WHERE state_abbrev = %(state)s
        OR name = %(state)s""",
        {"state": state},
    )

    try:
        state_abbrev = await res.fetchone()
        return state_abbrev["id"]
    except TypeError:
        return None


async def get_country_id(country_name: str, cur: psycopg.AsyncCursor) -> int:
    """Get id based on country."""
    res = await cur.execute(
        """SELECT id FROM countries WHERE name = %s""",
        (country_name,),
    )

    try:
        country = await res.fetchone()
        return country["id"]
    except TypeError:
        return None


async def get_continent_by_country(country: int, cur: psycopg.AsyncCursor) -> int:
    """Get ID of continent by country."""
    res = await cur.execute(
        """
        SELECT continent FROM countries WHERE id = %s
        """,
        (country,),
    )

    try:
        continent = await res.fetchone()
        return continent["continent"]
    except TypeError:
        return None


async def update_venue_count(pool: AsyncConnectionPool) -> None:
    """Update VENUES with number of events."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """
                UPDATE "venues" SET num_events=0, first_played=NULL, last_played=NULL;

                UPDATE "venues"
                    SET
                        num_events = t.num,
                        first_played = t.first_played,
                        last_played = t.last_played
                    FROM (
                    SELECT
                        v.id,
                        count(e.venue_id) AS num,
                        MIN(e.event_id) AS first_played,
                        MAX(e.event_id) AS last_played
                    FROM "venues" v
                    LEFT JOIN "events" e ON e.venue_id = v.id
                    WHERE e.event_id IS NOT NULL
                    GROUP BY v.id
                    ORDER BY v.id
                    ) t
                    WHERE "venues".id = t.id""",
            )

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)
        else:
            print("Updated VENUES with count of events")


async def venue_name_fix(venue_name: str) -> str:
    """Fix venue names which are formatted incorrectly on the site."""
    match venue_name:
        case "Alvin Theatre New York City Ny":
            return "Alvin Theatre, New York City, NY"
        case "Gwinnett Civic Center Arena Duluth Ga":
            return "Gwinnett Civic Center Arena, Duluth, GA"
        case "John F. Kennedy Memorial Center For The Performing Arts,Washington, DC":
            return "John F. Kennedy Memorial Center For The Performing Arts, Washington, DC"  # noqa: E501
        case _:
            return venue_name


async def venue_parser(
    venue_name: str,
    venue_url: str,
    cur: psycopg.AsyncCursor,
) -> dict[str]:
    """Parse venue name and return list of its components."""
    venue_dict = {
        "id": venue_url,
        "name": None,
        "city": None,
        "state": None,
        "country": None,
        "continent": None,
        "detail": None,
    }

    # fixes venue names that aren't correct
    fixed_name = await venue_name_fix(venue_name)

    # some venue names have prefixes at the end like (The) or (Le).
    # this is the easiest way I've found to grab that and bring it
    # to the front and remove the parenthesis
    try:
        match = re.search(r"(\((.+)\))", fixed_name)
        prefix = re.escape(match[1])
        venue_name = f"{match[2]} {re.sub(rf'\s*{prefix}\s*', '', fixed_name)}"
    except TypeError:
        venue_name = re.sub(r"([()])", "", fixed_name)

    # looks for venues that have either 3 or 4 comma separated components
    if match := re.search(r"^(.*),\s(.*),\s(.*)(?:,.+)?$", venue_name):
        # fix weird encodings and strip all components
        matches = [ftfy.fix_text(m.strip()) for m in match.groups()]

        venue_dict["name"] = matches[0]
        venue_dict["city"] = await get_city_id(matches[1], cur)
        venue_dict["country"] = await get_country_id(matches[-1], cur)

        # australia has states, apparently
        # and the venues can have 4 parts because of it
        if matches[-1] == "Australia":
            # splits the match again to catch the AUS location format
            # VENUE, CITY, STATE, AUS
            match_split = matches[0].split(", ")

            venue_dict["name"] = match_split[0]
            venue_dict["city"] = await get_city_id(match_split[1], cur)
            venue_dict["state"] = await get_state_id(matches[-2], cur)

        # US state abbreviations are two chars long
        if re.search(r"^\w{2}$", matches[-1]):
            venue_dict["state"] = await get_state_id(matches[-1].upper(), cur)

            # uses the states table and grabs the proper country name
            country = await get_country_from_abbrev(
                matches[-1],
                cur,
            )

            # finds the proper country id given the country
            venue_dict["country"] = await get_country_id(country, cur)

        # getting continent based on country
        venue_dict["continent"] = await get_continent_by_country(
            venue_dict["country"],
            cur,
        )

    return venue_dict


async def get_venues(pool: AsyncConnectionPool) -> None:
    """Get a list of venues from Brucebase, and inserts into the database."""
    response = await scraper.post("17778201")

    if response:
        soup = bs4(response, "lxml")
        links = await html_parser.get_clean_links(soup, "/venue:")

    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        venues = [await venue_parser(link["text"], link["url"], cur) for link in links]

        res = await cur.execute("""SELECT distinct brucebase_url FROM venues""")

        # not the ideal way to do this. But, without this check, it will
        # insert every single url whether there is a detail or not
        existing = [v["brucebase_url"] for v in await res.fetchall()]

        for venue in venues:
            if venue["id"] not in existing:
                try:
                    await cur.execute(
                        """INSERT INTO "venues"
                            (brucebase_url, name, city, state, country, continent, detail)
                            VALUES (%(id)s, %(name)s, %(city)s, %(state)s, %(country)s,
                                %(continent)s, %(detail)s)
                            ON CONFLICT (brucebase_url, name, detail)
                            DO NOTHING RETURNING *""",
                        venue,
                    )
                except (psycopg.OperationalError, psycopg.IntegrityError) as e:
                    print("VENUES: Could not complete operation:", e)

        print("Got Venues")
