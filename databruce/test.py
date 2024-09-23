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
    "/gig:1967-09-00-cafe-wha-new-york-city-ny": "/gig:1967-09-00b-cafe-wha-new-york-city-ny",
    "/gig:1968-05-00-left-foot-freehold-nj": "/gig:1968-05-00b-left-foot-freehold-nj",
    "/gig:1968-06-22-off-broad-street-coffee-house-red-bank-nj-early": "/gig:1968-06-22a-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-06-22-off-broad-street-coffee-house-red-bank-nj-late": "/gig:1968-06-22b-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-07-17-off-broad-street-coffee-house-red-bank-nj-early": "/gig:1968-07-17a-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-07-17-off-broad-street-coffee-house-red-bank-nj-late": "/gig:1968-07-17b-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-08-09-off-broad-street-coffee-house-red-bank-nj-early": "/gig:1968-08-09a-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-08-09-off-broad-street-coffee-house-red-bank-nj-late": "/gig:1968-08-09b-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-08-16-off-broad-street-coffee-house-red-bank-nj-early": "/gig:1968-08-16a-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-08-16-off-broad-street-coffee-house-red-bank-nj-late": "/gig:1968-08-16b-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-09-13-off-broad-street-coffee-house-red-bank-nj-early": "/gig:1968-09-13a-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-09-13-off-broad-street-coffee-house-red-bank-nj-late": "/gig:1968-09-13b-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-09-28-off-broad-street-coffee-house-red-bank-nj-early": "/gig:1968-09-28a-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-09-28-off-broad-street-coffee-house-red-bank-nj-late": "/gig:1968-09-28b-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-11-00-off-broad-street-coffee-house-red-bank-nj": "/gig:1968-11-00-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-12-20-off-broad-street-coffee-house-red-bank-nj-early": "/gig:1968-12-20a-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1968-12-20-off-broad-street-coffee-house-red-bank-nj-late": "/gig:1968-12-20b-off-broad-street-coffee-house-red-bank-nj",
    "/gig:1969-05-28-pandemonium-wanamassa-nj-early": "/gig:1969-05-28a-pandemonium-wanamassa-nj",
    "/gig:1969-05-28-pandemonium-wanamassa-nj-late": "/gig:1969-05-28b-pandemonium-wanamassa-nj",
    "/gig:1969-05-28-pandemonium-wanamassa-nj-third": "/gig:1969-05-28c-pandemonium-wanamassa-nj",
    "/nogig:1995-11-22-stone-pony-asbury-park-nj": "/nogig:1995-11-22b-stone-pony-asbury-park-nj",
}


with load_db() as conn:
    events = conn.execute(
        """SELECT event_id FROM events e WHERE event_id NOT IN
            (SELECT event_id FROM event_details) ORDER BY event_id""",
    ).fetchall()

    # "band",
    # "event_certainty", - confirmed
    # "event_id",
    # "event_title",
    # "event_type", - concert
    # "publicity",
    # "setlist_certainty",
    # "setlist_note",
    # "tour"

    band = conn.execute("""SELECT band_i""")
