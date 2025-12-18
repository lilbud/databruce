import asyncio

import numpy as np
import pandas as pd
import titlecase
from bs4 import BeautifulSoup as bs4

from databruce.database.db import load_db
from databruce.tools.scraping import scraper


def main() -> None:
    """Get release track table from brucebase page."""
    client = scraper.get_client()

    with client:
        response = scraper.get(
            "http://brucebase.wikidot.com/retail:the-collection-1973-84",
            client,
        )

        with load_db() as conn:
            cur = conn.cursor()

            if response:
                soup = bs4(response.content, "lxml")
                full = pd.DataFrame()

                table = soup.select(
                    """#wiki-tabview-f60998d658ca30e2509468dec9697617 >
                    div:nth-child(2) > div:nth-child(7) > table:nth-child(1)""",
                )

                for t in table:
                    df = pd.read_html(str(t), extract_links="body")[0]

                    full = pd.concat([full, df], ignore_index=True)

                full.index = np.arange(1, len(full) + 1)
                full.columns = ["num", "title", "time", "release"]
                release_id = 75

                for index, row in enumerate(full.itertuples(), start=65):
                    if row.title[1]:
                        song = cur.execute(
                            """SELECT id FROM songs WHERE brucebase_url = %s""",
                            (row.title[1],),
                        ).fetchone()["id"]

                        print(release_id, row.title[1][6:], song, index)

                        cur.execute(
                            """INSERT INTO release_tracks (release_id, track_num, song_id) VALUES (%s, %s, %s)""",
                            (release_id, index, song),
                        )
