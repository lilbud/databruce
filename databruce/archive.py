import datetime

import httpx
import psycopg
from psycopg.rows import dict_row
from tools.scraping import scraper


def get_list_from_archive(
    cur: psycopg.Cursor,
    client: httpx.Client,
) -> None:
    """Get all items from the Radio Nowhere collection and insert if missing."""
    response = scraper.get(
        "https://archive.org/advancedsearch.php?q=collection%3A%22radionowhere%22&fl[]=identifier&fl[]=databruce_id&fl[]=publicdate&sort[]=publicdate+asc&sort[]=&sort[]=&rows=2000&page=1&output=json",
        client,
    )

    if response:
        try:
            for item in response.json()["response"]["docs"]:
                event_id = cur.execute("""select id from events where event_id = %s""", (item["databruce_id"] ,)).fetchone()["id"]

                created_at = datetime.datetime.strptime(  # noqa: DTZ007
                    item["publicdate"],
                    "%Y-%m-%dT%H:%M:%SZ",
                )
                url = f"{item['identifier']}"

                cur.execute(
                    """INSERT INTO archive_links (event_id, archive_url, created_at)
                    VALUES (%s, %s, %s) ON CONFLICT (event_id, archive_url) DO NOTHING""",  # noqa: E501
                    (event_id, url, created_at),
                )
        except (psycopg.OperationalError, psycopg.IntegrityError) as e:
            print("ARCHIVE: Could not complete operation:", e)
        else:
            print("Got Archive List")
