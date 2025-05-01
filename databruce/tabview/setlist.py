"""Functions to handle the "Setlist" tab of an event page."""

import re

import psycopg
from bs4 import ResultSet, Tag
from titlecase import titlecase

EVENT_TYPES = "/(gig|nogig|interview|rehearsal|nobruce|recording):"


async def check_event_tags(
    event_id: str,
    song_tag: str,
    cur: psycopg.AsyncCursor,
) -> bool:
    """Check TAGS by event_id for specified special song tag."""
    res = await cur.execute(
        """SELECT event_id FROM "tags" WHERE %s = ANY(string_to_array(tags, ', '))
            AND event_id=%s""",
        (song_tag, event_id),
    )

    return bool(await res.fetchone())


async def get_set_name_from_url(event_url: str) -> str:
    """Return the url 'category', which is the default set name."""
    try:
        return titlecase(re.search(EVENT_TYPES, event_url).group(1))
    except re.error:
        return "Show"


async def get_event_date_from_url(event_url: str) -> str:
    """Return the event date from a given URL."""
    try:
        return re.search(r"\d{4}-\d{2}-\d{2}", event_url).group(0)
    except re.error:
        return None


async def get_event_from_db(event_url: str, cur: psycopg.AsyncCursor) -> str:
    """Return the event_id from the database for the given event_url."""
    res = await cur.execute(
        """SELECT event_id AS id FROM "events" WHERE brucebase_url=%s""",
        (event_url,),
    )

    try:
        event = await res.fetchone()
        return event["id"]
    except IndexError:
        return ""


async def song_id_corrector(
    song_url: str,
) -> str:
    """Corrects ids that don't match up to SONGS table."""
    match song_url:
        case "/song:rainy-day-women#12%20&%2035" | "/song:rainy-day-women#12 & 35":
            return "/song:rainy-day-women"
        case "/song:born-in-the-usa":
            return "/song:born-in-the-u-s-a"
        case _:
            return song_url


def clean_song_note(song_note: Tag) -> str:
    """Clean the song note with regex. Removes parenthesis and whitespace."""
    try:
        return re.sub(r"^[\s\(\)]|[\s\(\)]$", "", song_note.span.get_text())
    except AttributeError:
        return None


async def get_song_note(song: dict, segue: bool) -> str:  # noqa: FBT001
    """Return the note attached to a list element.

    It will only return a note for a single li item.
    """
    if segue:
        return None

    try:
        notes = [song["note"], titlecase(clean_song_note(song["link"]))]

        return ", ".join(filter(None, notes))
    except TypeError:
        return None


async def is_song_segue(i: int, list_size: int) -> bool:
    """Compare item position in element to total number of items in element.

    A segue is an unbroken chain from one song to the next (Ex. Incident > Rosie).
    Brucebase will list them as multiple items in an li element.
    This checks if a li element has multiple, and if the current item position
    is less than the total.
    """
    return i <= (list_size - 2)


def check_set_order(header_list: list[Tag]) -> list:
    """Get the proper order of sets by returning a list of the set_header p elements."""
    return [titlecase(p.get_text()) for p in header_list]


def rearrange_sets(setlist: dict, proper_set_order: list) -> dict:
    """Occasionally the setlists will be in the wrong order.

    usually putting soundcheck at the end, even when it is inserted first.
    Haven't figured out why, but in the meantime, this function will reorganize the
    setlist dict into the proper order based on the headers in the setlist tab.
    """
    return {set_name: setlist[f"{set_name}"] for set_name in proper_set_order}


async def parse_setlists(
    tab_content: Tag,
    default_set_name: str,
) -> dict[str, list]:
    """Parse tab content into lists based on set name."""
    sets = {}

    # the below was added because if there are no P headers in setlist tab
    # then it is believed that there is no setlist

    proper_set_order = [f"{default_set_name}"]

    if len(tab_content.find_all("p")) > 1:
        proper_set_order = check_set_order(tab_content.find_all("p"))
    else:
        sets = {f"{default_set_name}": []}
        current_set_name = default_set_name

    for item in tab_content.find_all(re.compile("^(p|ul|ol)$")):
        if item.name == "p" and item.strong:
            current_set_name = titlecase(item.get_text().strip(":"))

            sets[f"{current_set_name}"] = item.find_all_next(
                re.compile("(ul|ol) > li"),
                limit=1,
            )
        else:
            for link in item.find_all("li", recursive=False):
                if link.find(["ul", "ol"]) and "li" not in link.parents:
                    for nested_link in link.find(["ul", "ol"]).find_all("li"):
                        song = {
                            "link": nested_link,
                            "note": link.contents[0].strip(),
                        }

                        if song not in sets[f"{current_set_name}"]:
                            sets[f"{current_set_name}"].append(
                                {
                                    "link": nested_link,
                                    "note": link.contents[0].strip(),
                                },
                            )
                elif not link.find_parents("li"):
                    song = {
                        "link": link,
                        "note": "",
                    }
                    if song not in sets[f"{current_set_name}"]:
                        sets[f"{current_set_name}"].append(
                            {
                                "link": link,
                                "note": "",
                            },
                        )

    # for some unknown reason, sometimes the sets will end up out of order
    # not sure why, but this function will ensure they match the proper order
    # as in the setlist tab

    return rearrange_sets(sets, proper_set_order)


async def get_song_id(url: str, cur: psycopg.AsyncCursor) -> int:
    """Get id for a given song_url."""
    try:
        res = await cur.execute(
            """SELECT id FROM songs WHERE brucebase_url = %s""",
            (url,),
        )

        song = await res.fetchone()
        return song["id"]
    except TypeError:
        return None


async def get_song_info(
    seq_song: Tag | str,
    song: Tag,
    sequence: ResultSet,
    cur: psycopg.AsyncCursor,
) -> list:
    """Get info about the provided song.

    Given an li setlist item, get the url, id, and segue status.
    """
    if isinstance(seq_song, Tag):
        song_url = await song_id_corrector(seq_song["href"])
        song_id = await get_song_id(song_url, cur)

    segue = await is_song_segue(sequence.index(seq_song), len(sequence))
    song_note = await get_song_note(song, segue)

    return song_id, song_note, segue


async def setlist_check(
    tab_content: Tag,
    event_id: str,
    cur: psycopg.AsyncCursor,
) -> None:
    """Check for incomplete setlists.

    Checks if the setlist tab of an event has a note regarding
    the setlist being incomplete. Then updates events with this info
    """
    if tab_content.find("em", string=re.compile(".*incomplete.*", re.IGNORECASE)):
        await cur.execute(
            """UPDATE "events" SET setlist_certainty=%s WHERE event_id=%s""",
            ("Incomplete", event_id),
        )


async def get_setlist(
    tab_content: Tag,
    event_id: str,
    event_url: str,
    cur: psycopg.AsyncCursor,
) -> None:
    """Get a list of songs played at a given event and insert into database."""
    setlist = []
    event_id = await get_event_from_db(event_url, cur)

    # the default set name is the page category in the URL
    default_set_name = await get_set_name_from_url(event_url)

    # finds only the necessary elements in the setlist tab
    # p > strong - set name (note: not always there)
    # ul/ol > li - song_list, can either be ul or ol
    sets = await parse_setlists(tab_content, default_set_name)

    # checks setlist tab for note on incomplete setlist.
    # updates EVENTS to say either 'CONFIRMED' or 'INCOMPLETE'
    await setlist_check(tab_content, event_id, cur)

    for set_name, set_items in sets.items():
        for index, item in enumerate(set_items, 1):
            sequence = item["link"].text.split(" - ")

            if item["link"].a:
                sequence = item["link"].find_all("a", href=re.compile("/song:"))

            for seq_song in sequence:
                song_id, song_note, segue = await get_song_info(
                    seq_song,
                    item,
                    sequence,
                    cur,
                )

                current = [event_id, set_name, index, song_id, song_note, segue]

                if current not in setlist:
                    setlist.append(current)

    if len(setlist) == 0:
        await cur.execute(
            """UPDATE "events" SET setlist_certainty='Unknown'
                WHERE event_id=%s""",
            (event_id,),
        )

        print(f"No setlist available for {event_url}")
    else:
        await cur.execute(
            """UPDATE "events" SET setlist_certainty='Confirmed'
                WHERE event_id=%s""",
            (event_id,),
        )

        await cur.executemany(
            """INSERT INTO "setlists"
                    (event_id, set_name, song_num, song_id, song_note, segue)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT(event_id, song_num, song_id)
                    DO NOTHING""",
            (setlist),
        )

        print(f"setlist table updated for {event_url}")
