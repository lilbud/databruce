import re

import httpx
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


async def get_covers(pool: AsyncConnectionPool) -> None:
    """Grab a list of covers from my site and insert into database."""
    async with httpx.AsyncClient() as client:
        base_url = "https://raw.githubusercontent.com/lilbud/Bootleg_Covers/main"

        try:
            r = await client.get(
                "https://api.github.com/repos/lilbud/Bootleg_Covers/git/trees/main?recursive=1",
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",  # noqa: E501
                },
            )

            response = r.json()
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")

    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        for img in response["tree"]:
            if "Bruce_Springsteen" in img["path"] and re.search(
                "(.jpg|.png)$",
                img["path"],
            ):
                date = re.search(r"\d{4}-\d{2}-\d{2}", img["path"])[0]
                url = f"{base_url}/{img['path']}"

                try:
                    await cur.execute(
                        """INSERT INTO "covers" (event_date, cover_url)
                            VALUES (%(date)s, %(url)s)
                            ON CONFLICT(cover_url) DO NOTHING""",
                        {"date": date, "url": url},
                    )
                except (
                    psycopg.OperationalError,
                    psycopg.IntegrityError,
                ) as e:
                    print("COVERS: Could not complete operation:", e)

        print("Got Covers")
