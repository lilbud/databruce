import re
import time

from database import db
from geopy.geocoders import MapBox, Nominatim, OpenCage
from opencage.geocoder import OpenCageGeocode

key = "b1be54c5a825441fbba77fd7f3787749"
geocoder = OpenCage(key)


def geocode_venues(api_key):
    # Use the MapBox geocoder
    geolocator = Nominatim(user_agent="databruce_app")

    with db.load_db() as conn, conn.cursor() as cur:
        venues = cur.execute(
            """
            select
            v.id,
            v.name,
            c.name as city,
            s.name as state,
            c1.name as country,
            v.address
            from venues v
            left join cities c on c.id = v.city
            left join states s on s.id = c.state
            left join countries c1 on c1.id = c.country
            where v.name NOT LIKE '%Unknown%'
            and v.tried = false
            order by v.name
            """,
        ).fetchall()

        success_count = 0
        fail_count = 0

        print(len(venues), "venues to geocode")

        for venue in venues:
            query_parts = [venue['name'], venue["city"]]

            if venue["state"] and venue["state"] != venue["city"]:
                query_parts.append(venue["state"])

            query_parts.append(venue["country"])

            full_query = ", ".join(filter(None, query_parts))

            print(f"Geocoding: {full_query}")

            try:
                # permanent=True is a Mapbox-specific parameter for DB storage
                location = geolocator.geocode(full_query, timeout=10, addressdetails=True)

                if location:

                    details = location.raw.get('address', {})
    
                    # Extract only the bits you actually want
                    road = details.get('road', '')
                    house_number = details.get('house_number', '')
                    city = details.get('city') or details.get('town') or details.get('village', '')
                    state = details.get('state', '')
                    postcode = details.get('postcode', '')
                    country = details.get('country', '')

                    address_parts = []

                    if house_number and road:
                        address_parts.append(f"{house_number} {road}")
                    elif road:
                        address_parts.append(road)
                        
                    address_parts.extend([city, state, postcode])
                    
                    clean_address = ", ".join([p for p in address_parts if p])

                    # print(clean_address)
                    print(f"Geocoded: {venue['name']}")
                    print(
                        f"long: {location.longitude}, lat: {location.latitude}, addr: {clean_address}",
                    )

                    cur.execute(
                        """update venues set tried = true, latitude = %(latitude)s, longitude = %(longitude)s, address = %(address)s where id = %(id)s""",
                        {
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                            "address": clean_address,
                            "id": venue["id"],
                        },
                    )

                    success_count += 1
                else:
                    print(f"Could not geocode {venue['name']}")
                    fail_count += 1

                    cur.execute(
                        """update venues set no_match = true where id = %(id)s""",
                        {
                            "id": venue["id"],
                        },
                    )

            except Exception as e:
                print(f"Error geocoding {venue['name']}: {e}")
                continue

            print("---")
            conn.commit()

            time.sleep(1)

        print(f"Success Count: {success_count}")
        print(f"Fail Count: {fail_count}")


geocode_venues("b1be54c5a825441fbba77fd7f3787749")
