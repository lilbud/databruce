import datetime

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from tools.scraping import scraper


async def get_list_from_archive(pool: AsyncConnectionPool) -> None:
    """Get all items from the Radio Nowhere collection and insert if missing."""
    response = await scraper.get(
        "https://archive.org/advancedsearch.php?q=collection%3A%22radionowhere%22&fl[]=identifier&fl[]=databruce_id&fl[]=publicdate&sort[]=publicdate+asc&sort[]=&sort[]=&rows=2000&page=1&output=json",
    )

    if response:
        async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            try:
                for item in response.json()["response"]["docs"]:
                    event_id = item["databruce_id"]
                    created_at = datetime.datetime.strptime(  # noqa: DTZ007
                        item["publicdate"],
                        "%Y-%m-%dT%H:%M:%SZ",
                    )
                    url = f"https://archive.org/details/{item['identifier']}"

                    cur.execute(
                        """INSERT INTO archive_links (event_id, archive_url, created_at)
                        VALUES (%s, %s, %s) ON CONFLICT (event_id, archive_url) DO NOTHING""",  # noqa: E501
                        (event_id, url, created_at),
                    )
            except (psycopg.OperationalError, psycopg.IntegrityError) as e:
                print("ARCHIVE: Could not complete operation:", e)
            else:
                print("Got Archive List")
