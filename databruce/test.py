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
    "gig:2003-09-20-darien-lake-performing-arts-center-darien-ny": "gig:2003-09-20b-darien-lake-performing-arts-center-darien-ny",
    "gig:2003-09-20b-darien-lake-performing-arts-center-darien-ny": "gig:2003-09-20b-lake-performing-arts-center-darien-ny",
    "gig:2004-04-18-hit-factory-new-york-city-ny-early": "gig:2004-04-18a-hit-factory-new-york-city-ny",
    "gig:2004-04-18-hit-factory-new-york-city-ny-late": "gig:2004-04-18b-hit-factory-new-york-city-ny",
    "gig:2004-10-28-capitol-square-madison-wi": "gig:2004-10-28a-capitol-square-madison-wi",
    "gig:2004-10-28-south-oval-columbus-oh": "gig:2004-10-28b-south-oval-columbus-oh",
    "gig:2004-12-19-harry-s-roadhouse-asbury-park-nj-early": "gig:2004-12-19a-harry-s-roadhouse-asbury-park-nj",
    "gig:2004-12-19-harry-s-roadhouse-asbury-park-nj-late": "gig:2004-12-19b-harry-s-roadhouse-asbury-park-nj",
    "gig:2006-06-05-studio-3-nbc-studios-burbank-ca": "gig:2006-06-05a-nbc-studios-burbank-ca",
    "gig:2006-06-05-greek-theatre-los-angeles-ca": "gig:2006-06-05b-greek-theatre-los-angeles-ca",
    "gig:2008-04-21-united-methodist-church-red-bank-nj": "gig:2008-04-21a-united-methodist-church-red-bank-nj",
    "gig:2008-06-18-kennedy-center-washington-dc": "gig:2008-06-18a-kennedy-center-washington-dc",
    "gig:2008-06-18-arena-amsterdam-netherlands": "gig:2008-06-18b-arena-amsterdam-netherlands",
    "gig:2008-06-23-sportpaleis-antwerp-belgium": "gig:2008-06-23b-sportpaleis-antwerp-belgium",
    "gig:2009-03-19-nep-studio-52-new-york-city-ny": "gig:2009-03-19a-nep-studios-new-york-city-ny",
    "gig:2009-03-21-ocean-place-resort-long-branch-nj": "gig:2009-03-21b-ocean-place-resort-long-branch-nj",
    "gig:2009-06-27-worthy-farm-pilton-england-afternoon": "gig:2009-06-27a-worthy-farm-pilton-england",
    "gig:2009-06-27-worthy-farm-pilton-england-evening": "gig:2009-06-27b-worthy-farm-pilton-england",
    "gig:2009-06-28-hyde-park-london-england-afternoon": "gig:2009-06-28a-hyde-park-london-england",
    "gig:2009-06-28-hyde-park-london-england-evening": "gig:2009-06-28b-hyde-park-london-england",
    "gig:1987-08-26-columns-avon-nj": "gig:1987-08-26b-columns-avon-nj",
    "gig:1987-10-08-ritz-new-york-city-ny": "gig:1987-10-08b-ritz-new-york-city-ny",
    "gig:1990-02-12-greenacres-beverly-hills-ca": "gig:1990-02-12a-greenacres-beverly-hills-ca",
    "gig:1990-02-12-china-club-hollywood-ca": "gig:1990-02-12b-china-club-hollywood-ca",
    "gig:1993-05-16-alter-flughafen-riem-munich-germany": "gig:1993-05-16a-alter-flughafen-riem-munich-germany",
    "gig:1993-05-16-hotel-bayerischer-hof-munich-germany": "gig:1993-05-16b-hotel-bayerischer-hof-munich-germany",
    "gig:1995-04-05-ed-sullivan-theater-new-york-city-ny": "gig:1995-04-05a-ed-sullivan-theater-new-york-city-ny",
    "gig:1995-04-05-sony-music-studios-new-york-city-ny": "gig:1995-04-05b-sony-music-studios-new-york-city-ny",
    "gig:1995-05-00-private-residence-beverly-hills-ca": "gig:1995-05-00b-private-residence-beverly-hills-ca",
    "gig:1995-11-27-nbc-studios-burbank-ca": "gig:1995-11-27a-nbc-studios-burbank-ca",
    "gig:1995-11-27-wiltern-theatre-los-angeles-ca": "gig:1995-11-27b-wiltern-theatre-los-angeles-ca",
    "gig:1996-10-02-riverside-theater-milwaukee-wi": "gig:1996-10-02a-riverside-theater-milwaukee-wi",
    "gig:1996-10-02-bradley-center-milwaukee-wi": "gig:1996-10-02b-bradley-center-milwaukee-wi",
    "gig:1997-01-27-kokusai-foramu-tokyo-japan": "gig:1997-01-27b-kokusai-foramu-tokyo-japan",
    "gig:1998-12-14-tve-studios-madrid-spain": "gig:1998-12-14c-tve-studios-madrid-spain",
    "gig:2001-08-18-waterfront-asbury-park-nj": "gig:2001-08-18a-waterfront-asbury-park-nj",
    "gig:2001-08-18-stone-pony-asbury-park-nj": "gig:2001-08-18b-stone-pony-asbury-park-nj",
    "gig:2002-07-26-sonny-s-southern-cuisine-asbury-park-nj": "gig:2002-07-26b-sonny-s-southern-cuisine-asbury-park-nj",
    "gig:2002-10-04-zakim-bridge-boston-ma": "gig:2002-10-04a-zakim-bridge-boston-ma",
    "gig:2002-10-04-fleetcenter-boston-ma": "gig:2002-10-04b-fleetcenter-boston-ma",
    "gig:1965-00-00-knights-of-columbus-freehold-nj": "gig:1965-00-00c-knights-of-columbus-freehold-nj",
    "gig:1965-00-00a-unknown-location-freehold-nj": "gig:1965-00-00d-unknown-location-freehold-nj",
    "gig:1965-00-00b-unknown-location-freehold-nj": "gig:1965-00-00e-unknown-location-freehold-nj",
    "gig:1965-00-00-regional-high-school-freehold-nj": "gig:1965-00-00f-regional-high-school-freehold-nj",
    "gig:1965-07-00-clearwater-swim-club-atlantic-highlands-nj": "gig:1965-07-00b-clearwater-swim-club-atlantic-highlands-nj",
    "gig:1965-08-00-woodhaven-swim-club-freehold-nj": "gig:1965-08-00a-woodhaven-swim-club-freehold-nj",
    "gig:1965-08-00-blue-moon-freewood-acres-nj": "gig:1965-08-00b-blue-moon-freewood-acres-nj",
    "gig:1965-08-00-st-rose-of-lima-school-freehold-nj": "gig:1965-08-00c-st-rose-of-lima-school-freehold-nj",
    "gig:1965-09-00-st-rose-of-lima-school-freehold-nj": "gig:1965-09-00a-st-rose-of-lima-school-freehold-nj",
    "gig:1965-09-00-angle-inn-farmingdale-nj": "gig:1965-09-00b-angle-inn-farmingdale-nj",
    "gig:1965-09-00-elks-lodge-freehold-nj": "gig:1965-09-00c-elks-lodge-freehold-nj",
    "gig:1965-10-00-recreation-hall-fort-monmouth-nj": "gig:1965-10-00a-recreation-hall-fort-monmouth-nj",
    "gig:1965-10-00-reception-hall-monmouth-county-nj": "gig:1965-10-00b-reception-hall-monmouth-county-nj",
    "gig:1965-10-00-state-hospital-marlboro-nj": "gig:1965-10-00c-state-hospital-marlboro-nj",
    "gig:1965-11-00-shoprite-freehold-nj": "gig:1965-11-00a-shoprite-freehold-nj",
    "gig:1965-11-00-st-rose-of-lima-school-freehold-nj": "gig:1965-11-00b-st-rose-of-lima-school-freehold-nj",
    "gig:1985-03-31-qe-ii-brisbane-australia": "gig:1985-03-31b-qe-ii-brisbane-australia",
    "gig:1985-06-29-parc-de-la-courneuve-paris-france": "gig:1985-06-29b-parc-de-la-courneuve-paris-france",
    "gig:1985-06-30-parc-de-la-courneuve-paris-france": "gig:1985-06-30b-parc-de-la-courneuve-paris-france",
    "gig:1987-08-26-key-largo-belmar-nj": "gig:1987-08-26a-key-largo-belmar-nj",
    "gig:2024-07-09-dyrskueplads-odense-denmark": "gig:2024-07-09-dyrskuepladsen-odense-denmark",
    "gig:1967-11-00-first-presbyterian-church-freehold-nj": "gig:1967-11-00a-first-presbyterian-church-freehold-nj",
    "gig:1967-11-00b-cafe-wha-new-york-city-ny": "gig:1967-11-00c-cafe-wha-new-york-city-ny",
    "gig:1967-11-00a-cafe-wha-new-york-city-ny": "gig:1967-11-00b-cafe-wha-new-york-city-ny",
    "gig:1967-10-00-christian-brothers-academy-lincroft-nj": "gig:1967-10-00a-christian-brothers-academy-lincroft-nj",
    "gig:1967-08-00-unknown-location-howell-nj": "gig:1967-08-00c-unknown-location-howell-nj",
    "gig:1965-00-00-elks-lodge-freehold-nj": "gig:1965-00-00b-elks-lodge-freehold-nj",
}

with load_db() as conn:
    for old_url, new_url in fix.items():
        conn.execute(
            """UPDATE events SET brucebase_url = %(new_url)s WHERE brucebase_url = %(old_url)s RETURNING *""",
            {"old_url": old_url, "new_url": new_url},
        )
