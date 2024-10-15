import asyncio
import re
import time

import ftfy
import musicbrainzngs
from database import db
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from thefuzz import fuzz, process

musicbrainzngs.set_useragent("Chrome", "37.0.2062.94", contact=None)


async def get_venues(pool: AsyncConnectionPool) -> None:
    """Mark song premieres and tour debuts."""
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        res = await cur.execute(
            """
            SELECT
                v.id,
                v.mb_id
            FROM venues v
            WHERE v.mb_id IS NOT NULL
            ORDER BY name
            """,
        )

        return await res.fetchall()


def compare_to_aliases(query: str, alias_list: list) -> bool:
    """Get the list of aliases for the given id, compare venue name to list."""
    score = process.extractOne(query, alias_list)

    if score[1] == 100:  # noqa: PLR2004
        return True

    return False


def check_name(db_name: str, result_name: str) -> bool:  # noqa: D103
    ratio = fuzz.ratio(db_name.lower(), result_name.lower())

    print(ratio)

    if ratio >= 95:  # noqa: PLR2004
        return True

    return False


def check_area(city: str, area: dict) -> bool:  # noqa: D103
    try:
        if process.extractOne(city, [area["name"], area["sort-name"]])[1] == 100:  # noqa: PLR2004
            return True

    except KeyError:
        return False
    else:
        return False


def get_aliases_by_id(mbid: str) -> str:  # noqa: D103
    result = musicbrainzngs.get_place_by_id(mbid, includes=["aliases"])

    try:
        return ", ".join(
            sorted([i["sort-name"] for i in result["place"]["alias-list"]]),
        )
    except KeyError:
        return ""


async def mb_place_search(query: str, name: str, city: str) -> str:  # noqa: D103
    result = musicbrainzngs.search_places(query, area=city)

    for r in result["place-list"]:
        try:
            alias_list = [i["sort-name"] for i in r["alias-list"]]

            if compare_to_aliases(name, alias_list):
                return r["id"]

        except KeyError:
            if r["ext:score"] == "100" and "area" in r and check_area(city, r):
                return r["id"]
            return None

    return None


async def main(pool: AsyncConnectionPool) -> None:  # noqa: D103
    async with pool as pool:
        venues = await get_venues(pool)

        async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            for venue in venues:
                query = " ".join(
                    filter(None, [venue["name"], venue["city"]]),
                )

                result = await mb_place_search(
                    query,
                    venue["name"],
                    venue["city"],
                    venue["state"],
                )

                if result:
                    print(venue["name"], venue["city"], result)
                    await cur.execute(
                        """UPDATE venues SET mb_id = %s WHERE id = %s""",
                        (result, venue["id"]),
                    )

                else:
                    print(venue["name"], venue["city"])
                    await cur.execute(
                        """UPDATE venues SET mb_id = NULL WHERE id = %s""",
                        (venue["id"],),
                    )

                await conn.commit()

            await asyncio.sleep(0.5)


async def venue_aliases(pool: AsyncConnectionPool) -> None:  # noqa: D103
    async with pool as pool:
        venues = await get_venues(pool)

        async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            for venue in venues:
                aliases = get_aliases_by_id(venue["mb_id"])

                if aliases != "":
                    print(aliases)
                    await cur.execute(
                        """UPDATE venues SET aliases = %s WHERE id = %s""",
                        (aliases, venue["id"]),
                    )

                await conn.commit()


with db.load_db() as conn:
    cur = conn.cursor()

    res = cur.execute(
        """
        SELECT
           s.id,
           s.song_name,
           s.mbid
        FROM songs s
        WHERE s.mbid IS NOT NULL
        ORDER BY s.song_name
        """,
    ).fetchall()

    songs = []

    for r in res:
        db_id = r["id"]
        db_name = r["song_name"]
        mbid = r["mbid"]

        print(db_name, mbid)

        result = musicbrainzngs.get_work_by_id(id=mbid, includes=["artist-rels"])[
            "work"
        ]

        if result:
            new_name = ftfy.fix_text(result["title"])

            print(db_name, " / ", new_name)

            cur.execute(
                """UPDATE songs SET song_name = %s WHERE id=%s""",
                (new_name, db_id),
            )

        print()

        time.sleep(0.5)
