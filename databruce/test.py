"""File for testing random code/functions/ideas."""

import asyncio
import json
import re
from pathlib import Path

import ftfy
from bs4 import BeautifulSoup as bs4
from database.db import load_db
from dotenv import load_dotenv
from tools.scraping import scraper

load_dotenv()

# from tags.tags import get_tags

# musicbrainzngs.set_useragent("Chrome", "37.0.2062.94", contact=None)

# conn = db.load_db()

# geolocator = Nominatim(user_agent="Chrome 37.0.2062.94")

# location = geolocator.geocode("Abidjan		Ivory Coast")

# print(location.raw)


# async def main():
#     test = "Burnin’ Train"

#     print(ftfy.fix_text(test))


# asyncio.run(main())
venues = [
    "television-centre-london-england",
    "anfield-liverpool-england",
    "david-geffen-theater-los-angeles-ca",
    "museum-of-modern-art-new-york-city-ny",
    "co-op-live-manchester-england",
    "reale-arena-donostia-san-sebastian-spain",
    "decathlon-arena-villeneuve-d-ascq-france",
]

with load_db() as conn:
    events = conn.execute(
        """SELECT brucebase_url AS id FROM events WHERE venue_id IS NULL""",
    ).fetchall()

    for event in events:
        venue_url = re.sub(r"/.*:\d{4}-\d{2}-\d{2}-", "", event["id"])

        venue = conn.execute(
            """SELECT id FROM venues WHERE brucebase_url = %s""",
            (venue_url,),
        ).fetchone()

        if venue:
            venue_id = venue["id"]

            conn.execute(
                """UPDATE events SET venue_id = %s WHERE brucebase_url = %s""",
                (venue_id, event["id"]),
            )
