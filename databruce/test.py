"""File for testing random code/functions/ideas."""

from database.db import load_db
from dotenv import load_dotenv

load_dotenv()

# from tags.tags import get_tags

# musicbrainzngs.set_useragent("Chrome", "37.0.2062.94", contact=None)

# conn = db.load_db()

# geolocator = Nominatim(user_agent="Chrome 37.0.2062.94")

# location = geolocator.geocode("Abidjan		Ivory Coast")

# print(location.raw)

fix = {
    "bruce-springsteen": "Lead vocal, electric and acoustic guitars, harmonica",
    "roy-bittan": "Piano, keyboards",
    "nils-lofgren": "Electric and acoustic guitars, backing vocal",
    "garry-tallent": "Bass",
    "steven-van-zandt": "Electric and acoustic guitars, backing vocal",
    "max-weinberg": "Drums",
    "jake-clemons": "Tenor saxophone, percussion, backing vocal",
    "charlie-giordano": "Organ, keyboards",
    "soozie-tyrell": "Violin, acoustic guitar, percussion",
    "anthony-almonte": "Percussion, backing vocal",
    "ada-dyer": "Backing vocal",
    "curtis-king": "Backing vocal",
    "lisa-lowell": "Backing vocal",
    "michelle-moore": "Backing vocal",
    "barry-danielian": "Trumpet",
    "ed-manion": "Baritone and tenor saxophone",
    "ozzie-melendez": "Trombone",
    "curt-ramm": "Trumpet",
}


with load_db() as conn:
    for member, inst in fix.items():
        conn.execute(
            """UPDATE relations SET instruments=%s WHERE brucebase_url=%s""",
            (inst, member),
        )
