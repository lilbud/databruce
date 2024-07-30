"""File for testing random code/functions/ideas."""

import re
from pathlib import Path

import musicbrainzngs
import psycopg
from database import db
from geopy.geocoders import Nominatim

# from tags.tags import get_tags

# musicbrainzngs.set_useragent("Chrome", "37.0.2062.94", contact=None)

conn = db.load_db()

# geolocator = Nominatim(user_agent="Chrome 37.0.2062.94")

# location = geolocator.geocode("Abidjan		Ivory Coast")

# print(location.raw)


def get_location(date: str, conn: psycopg.Connection) -> str:
    res = conn.execute(
        """SELECT city FROM events_with_info WHERE event_date::text = %s""",
        (date,),
    ).fetchone()

    return res["city"]


info = Path(
    r"E:\\Media\\Music\\Bootlegs\\Bruce Springsteen\\_tosort\\compilations\2006 Tour - Swing That Thing\\mp3tag.txt",
)

base = info.parent
new_info = Path(base, "newinfo.txt")
lines = []

with conn:
    for i in info.read_text().split("\n"):
        line = i.strip()
        try:
            date = re.search(r"\d{4}-\d{2}-\d{2}", line)[0]
            song = re.sub(rf"\s*\({date}\)", "", line)
            location = get_location(date, conn)

            lines.append(f"{song} ({date} - {location})")

        except TypeError:
            lines.append(line)

with Path.open(new_info, "w") as file:
    for l in lines:
        file.write(f"{l}\n")
