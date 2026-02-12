import re

import httpx
import psycopg
from tools.scraping import scraper
from database import db

def get_covers(cur: psycopg.Cursor, client: httpx.Client) -> None:
    """Grab a list of covers from my site and insert into database."""
    base_url = "https://raw.githubusercontent.com/lilbud/Bootleg_Covers/main"

    try:
        r = scraper.get(
            "https://api.github.com/repos/lilbud/Bootleg_Covers/git/trees/main?recursive=1",
            client,
        )
        response = r.json()
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
    
    for img in response['tree']:
        if re.search(r"bruce.*\d{4}-\d{2}-\d{2}.*\.(jpg|png)$", img['path']):
            date = re.search("\d{4}-\d{2}-\d{2}", img['path'])[0]
            url = f"{base_url}/{img['path']}"

            event = cur.execute(
                """SELECT id FROM events WHERE event_date = %(date)s""",
                {"date": date},
            ).fetchone()['id']

            try:
                cur.execute(
                    """INSERT INTO "covers" (event_id, cover_url)
                        VALUES (%(event)s, %(url)s)
                        ON CONFLICT(cover_url) DO NOTHING""",
                    {"event": event, "url": url},
                )
            except (
                psycopg.OperationalError,
                psycopg.IntegrityError,
            ) as e:
                print("COVERS: Could not complete operation:", e.with_traceback())

    print("Got Covers")

if __name__ == "__main__":
    with db.load_db() as conn, conn.cursor() as cur, httpx.Client() as client:
        get_covers(cur, client)