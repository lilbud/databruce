"""Database utilities and functions.

Likely many of these aren't needed often, but I had to write them to
fix different issues, so here they are.

This module provides:
- get_song_name_from_db: returns the song_name for a given song_url
- update_song_by_tags: Update entries in SETLISTS if that event has a specific tag.
- update_on_stage_names: Update name columns in on_stage if empty and has url.
- update_event_locations: Update location columns in EVENTS based on venue_url.
- update_event_day: Update day of week in EVENTS based on the event date.
"""

from db import load_db


def update_song_by_tags() -> None:
    """Update entries in the SETLISTS table if that event has a specific tag.

    Tags (so far):
        pian78 - Prove It 1978
    """
    with load_db() as conn:
        res = conn.execute("""SELECT * FROM "TAGS";""").fetchall()

        for row in res:
            tags = row["tags"].split(", ")

            if "pian78" in tags:
                old_song_id = "prove-it-all-night"
                new_song_id = "prove-it-all-night-78"

                conn.execute(
                    """UPDATE SETLISTS SET song_id=%(new_id)s WHERE song_id=%(old_id)s
                        AND event_url=%(event)s""",
                    {
                        "new_id": new_song_id,
                        "old_id": old_song_id,
                        "event": row["event_id"],
                    },
                )
