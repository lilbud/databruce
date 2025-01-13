import asyncio
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
from database import db

file = Path(
    r"C:\Users\bvw20\Documents\Personal\Databruce Project\guests by event and song.csv",
)


df = pd.read_csv(file)


async def get_guest_id(name: pd.Series) -> int | None:
    with db.load_db() as conn:
        cur = conn.cursor()

        res = cur.execute(
            """SELECT id FROM relations WHERE relation_name=%s""",
            (name,),
        ).fetchone()

        try:
            return int(res["id"])
        except TypeError:
            return None


async def format_input():
    item = df.melt(
        id_vars=["event", "setlist_id"],
        var_name="guest",
        value_name="name",
    ).dropna()

    item = item.drop("guest", axis=1)

    guests = item["name"].unique().tolist()

    print(len(guests))

    for guest in guests:
        id = await get_guest_id(guest)

        if id:
            print(id)
            item.loc[(item["name"] == guest), "guest_id"] = id

    print(item.loc[item["name"] == ""])

    item.sort_values(["event", "setlist_id"]).to_csv(
        r"C:\Users\bvw20\Documents\Personal\Databruce Project\guests\guests.csv",
    )


async def insert() -> None:
    df = pd.read_csv(
        Path(r"C:\Users\bvw20\Documents\Personal\Databruce Project\guests\guests.csv"),
    )

    with db.load_db() as conn:
        cur = conn.cursor()

        cur.executemany(
            """INSERT INTO guests (event_id, setlist_id, guest_id) VALUES (%s, %s, %s)
                ON CONFLICT (event_id, setlist_id, guest_id) DO NOTHING""",
            (df.values.tolist()),  # noqa: PD011
        )


asyncio.run(insert())
