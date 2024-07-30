import re
import sqlite3
from pathlib import Path

db_path = Path(
    Path(__file__).parent.parent,
    "database",
    "database.sqlite",
)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

with conn:
    res = conn.execute(
        """SELECT DISTINCT(event_id) FROM SETLISTS ORDER BY event_id ASC""",
    ).fetchall()
    ssn = 1

    for row in res:
        song_num = 1
        setlist = conn.execute(
            """SELECT * FROM SETLISTS WHERE event_id = ? ORDER BY event_id, CAST(song_num AS INT)""",
            (row["event_id"],),
        ).fetchall()

        for song in setlist:
            event_id = song["event_id"]
            set_name = song["set_name"]
            song_id = song["song_id"]
            song_note = song["song_note"]
            segue = song["segue"]
            premiere = song["premiere"]
            debut = song["debut"]
            position = song["position"]
            last = song["last"]
            next = song["next"]

            repeat_value = re.search(r"(x?(\d)x?)", song_note)

            print(
                ssn,
                event_id,
                set_name,
                song_num,
                song_id,
                song_note,
                segue,
                premiere,
                debut,
                position,
                last,
                next,
            )

            if repeat_value and int(repeat_value[2]) > 1:
                for i in range(int(repeat_value[2])):
                    print(
                        ssn,
                        event_id,
                        set_name,
                        song_num,
                        song_id,
                        song_note,
                        segue,
                        premiere,
                        debut,
                        position,
                        last,
                        next,
                    )

                    conn.execute(
                        """INSERT OR IGNORE INTO SETLISTS_NEW VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (
                            ssn,
                            event_id,
                            set_name,
                            song_num,
                            song_id,
                            song_note,
                            segue,
                            premiere,
                            debut,
                            position,
                            last,
                            next,
                        ),
                    )
                    song_num += 1
                    ssn += 1
            else:
                conn.execute(
                    """INSERT INTO SETLISTS_NEW VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        ssn,
                        event_id,
                        set_name,
                        song_num,
                        song_id,
                        song_note,
                        segue,
                        premiere,
                        debut,
                        position,
                        last,
                        next,
                    ),
                )

                song_num += 1
                ssn += 1
