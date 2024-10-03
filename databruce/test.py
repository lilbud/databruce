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
    "Bruce Springsteen": "vocals, guitar, harmonica",
    "Roy Bittan": "piano, synthesizer",
    "Nils Lofgren": "guitar, vocals",
    "Garry Tallent": "bass guitar",
    "Steven Van Zandt": "guitar, vocals",
    "Max Weinberg": "drums",
    "Charlie Giordano": "keyboards",
    "Soozie Tyrell": "violin, guitar, vocals",
    "Anthony Almonte": "percussion, vocals",
    "Jake Clemons": "saxophone, vocals",
    "Barry Danielian": "trumpet, percussion",
    "Ada Dyer": "vocals, percussion",
    "Curtis King": "vocals, percussion",
    "Lisa Lowell": "vocals, percussion",
    "Eddie Manion": "saxophone, percussion",
    "Ozzie Melendez": "trombone, percussion",
    "Michelle Moore": "vocals, percussion",
    "Curt Ramm": "trumpet, percussion",
    "Patti Scialfa": "backing vocals, guitar",
}


with load_db() as conn:
    for member, inst in fix.items():
        conn.execute(
            """
            UPDATE "onstage"
            SET
                instruments=%(inst)s
            FROM (
                SELECT
                    o.id,
                    o.relation_id
                FROM onstage o
                LEFT JOIN event_details e ON e.event_id = o.event_id
                WHERE o.relation_id = %(member)s
                AND e.tour = '23int-tour'
            ) t
            WHERE "onstage".id=t.id AND "onstage".relation_id=t.relation_id;
            """,
            {"member": member.lower().replace(" ", "-"), "inst": inst},
        )

        conn.commit()
