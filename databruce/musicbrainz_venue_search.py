import asyncio

import musicbrainzngs
from database import db
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

musicbrainzngs.set_useragent("Chrome", "37.0.2062.94", contact=None)
from thefuzz import fuzz, process


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

    if score[1] == 100:
        return True

    return False


def check_name(db_name: str, result_name: str) -> bool:
    if fuzz.ratio(db_name, result_name) == 100:
        return True

    return False


def check_area(city: str, area: dict) -> bool:
    try:
        if process.extractOne(city, [area["name"], area["sort-name"]])[1] == 100:
            return True

        return False
    except KeyError:
        return False


def get_aliases_by_id(mbid: str) -> str:
    result = musicbrainzngs.get_place_by_id(mbid, includes=["aliases"])

    try:
        return ", ".join(
            sorted([i["sort-name"] for i in result["place"]["alias-list"]]),
        )
    except KeyError:
        return ""


async def mb_place_search(query: str, name: str, city: str, state: str) -> str:
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


async def main(pool: AsyncConnectionPool) -> None:
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
                        """UPDATE venues SET mb_id = %s, updated_at=now() WHERE id = %s""",
                        (result, venue["id"]),
                    )

                else:
                    print(venue["name"], venue["city"])
                    await cur.execute(
                        """UPDATE venues SET mb_id = '', updated_at=now() WHERE id = %s""",
                        (venue["id"],),
                    )

                await conn.commit()

            await asyncio.sleep(0.5)


async def venue_aliases(pool: AsyncConnectionPool) -> None:
    async with pool as pool:
        venues = await get_venues(pool)

        async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            for venue in venues:
                aliases = get_aliases_by_id(venue["mb_id"])

                if aliases != "":
                    print(aliases)
                    await cur.execute(
                        """UPDATE venues SET aliases = %s, updated_at=now() WHERE id = %s""",
                        (aliases, venue["id"]),
                    )

                await conn.commit()


if __name__ == "__main__":
    asyncio.run(venue_aliases(db.pool), loop_factory=asyncio.SelectorEventLoop)


# print(json.dumps(result, indent=2))

query = "Academy Of Music	Philadelphia"
venue = "Academy Of Music"
city = "Philadelphia"
state = "PA"

# result = asyncio.run(mb_place_search(query, venue, city, state))

# result = musicbrainzngs.search_places(query, area=city)


# if result["place-list"][0]["ext:score"] == "100":
#     print(result["place-list"][0])

# print(result)


# print(get_aliases_by_id("2b3e65a3-c269-461f-928c-c9f0cb9a7bbc"))
