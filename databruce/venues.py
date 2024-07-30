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
from locations.countries import get_country_from_abbrev
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from tools.parsing import html_parser
from tools.scraping import scraper


async def update_venue_count(pool: AsyncConnectionPool) -> None:
    """Update VENUES with number of events."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                """UPDATE "venues"
                    SET
                        num_events = t.num
                    FROM (
                    SELECT
                        v.id,
                        count(e.venue_id) AS num
                    FROM "venues" v
                    LEFT JOIN "events" e ON e.venue_id = v.brucebase_url
                    GROUP BY v.id
                    ORDER BY v.id
                    ) t
                    WHERE "venues".id = t.id""",
            )

        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("Could not complete operation:", e)


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
    }

    # fixes venue names that aren't correct
    fixed_name = await venue_name_fix(venue_name)

    try:
        match = re.search(r"(\((.+)\))", fixed_name)
        prefix = re.escape(match[1])
        venue_name = f"{match[2]} {re.sub(rf"\s*{prefix}\s*", "", fixed_name)}"
    except TypeError:
        venue_name = re.sub(r"([()])", "", fixed_name)

    # looks for venues that have either 3 or 4 comma separated components
    if match := re.search(r"^(.*),\s(.*),\s(.*)(?:,.+)?$", venue_name):
        # fix weird encodings and strip all components
        matches = [ftfy.fix_text(m.strip()) for m in match.groups()]

        venue_dict["name"] = matches[0]
        venue_dict["city"] = matches[1]
        venue_dict["country"] = matches[-1]

        # australia has states, apparently
        # and the venues can have 4 parts because of it
        if matches[-1] == "Australia":
            match_split = matches[0].split(", ")

            venue_dict["name"] = match_split[0]
            venue_dict["city"] = match_split[1]
            venue_dict["state"] = matches[-2]
            venue_dict["country"] = matches[-1]

        # state abbreviations are two chars long
        if re.search(r"^\w{2}$", matches[-1]):
            venue_dict["state"] = matches[-1].upper()
            venue_dict["country"] = await get_country_from_abbrev(
                matches[-1],
                cur,
            )

    return venue_dict


async def get_venues(pool: AsyncConnectionPool) -> None:
    """Get a list of venues from Brucebase, and inserts into the database."""
    response = await scraper.post("17778201")
    venues = []

    if response:
        soup = bs4(response, "lxml")
        links = await html_parser.get_clean_links(soup, "/venue:")

    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        venues = [await venue_parser(link["text"], link["url"], cur) for link in links]

        for venue in venues:
            try:
                await cur.execute(
                    """INSERT INTO "venues"
                        (brucebase_url, name, city, state, country)
                        VALUES (%(id)s,%(name)s,%(city)s,%(state)s,%(country)s)
                        ON CONFLICT (brucebase_url) DO UPDATE SET name=%(name)s,
                        city=%(city)s, state=%(state)s, country=%(country)s""",
                    venue,
                )
            except (psycopg.OperationalError, psycopg.IntegrityError) as e:
                print("Could not complete operation:", e)
