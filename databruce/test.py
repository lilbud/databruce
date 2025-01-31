"""File for testing random code/functions/ideas."""

import asyncio
import re
from pathlib import Path

import httpx
import pandas as pd
from database.db import load_db
from dotenv import load_dotenv
from tools.scraping import scraper

load_dotenv()
from bs4 import BeautifulSoup as bs4

# df = pd.read_csv(Path(r"E:\Media\Music\Bootlegs\_other\Millard.csv"), encoding="cp1252")

# unique_artists = df["artist"].unique().tolist()
# generations = df["generation"].unique().tolist()
# unique_dates = df["date"].unique().tolist()
# unique_locations = df["venue"].unique().tolist()

# print(f"Unique Artists: {len(unique_artists)}")
# print("\nGenerations:\n" + "-" * 20)

# for g in generations:
#     print(f"{g}: {len(df.loc[df["generation"] == g])}")

# print(f"\nUnique Shows: {len(unique_dates)}")
# print(f"\nUnique Locations: {len(unique_locations)}")


async def main(year: str):
    with httpx.Client() as client:
        response = await scraper.get(f"http://brucebase.wikidot.com/{year}")

        if response:
            soup = bs4(response.content, "lxml")

            for sec in str(soup.find("div", id="main-content")).split(
                "<hr>",
            ):
                section = bs4(sec, "lxml")
                songs = []
                for i in section.find_all("p"):
                    title = ""
                    if i.find(
                        "a",
                        href=re.compile("gig|rehearsal|nogig"),
                    ) and re.search(r"\d{4}-\d{2}-\d{2}", i.text):
                        title = re.search(r"\d{4}-\d{2}-\d{2}", i.text)[0]
                        print(f"{title}:")

                    text = i.get_text()

                    if "/" not in text and re.search(
                        "(sign|request)",
                        text,
                        flags=re.IGNORECASE,
                    ):
                        for sentence in text.split("."):
                            if re.search(
                                "(sign|request)",
                                sentence,
                                flags=re.IGNORECASE,
                            ):
                                for s in sentence.split(","):
                                    print(f"{s.strip()},")

                                print()


def read_signs():
    with Path.open(r"C:\Users\bvw20\Desktop\signs.txt", "r") as file:
        content = [line.strip("\n,") for line in file.readlines()]

        for show in content:
            date = show.split(":")[0]
            songs = show.split(":")[1].strip().split("/")

            for s in songs:
                print(date, ":", s)


def parser_scrape():
    url = "https://volkerzell.de/bruce/brucebase-report.html#org2f93f0a"

    with httpx.Client() as client:
        r = client.get(url)

        if r:
            soup = bs4(r.content, "lxml")

            venues = []

            table = soup.find("table", id="brucebase-events")

            df = pd.read_html(str(table))
            df[0].columns = [c.lower().replace(" ", "_") for c in df[0].columns]
            df[0].fillna("No Value", inplace=True)

            for i in df[0].itertuples():
                if i.venue_detail != "No Value":
                    url = re.sub("^venue:", "", i.detail_venue_url)
                    if i.venue.lower().replace(" ", "-") not in url:
                        current = [
                            url,
                            f"{i.venue.strip("'")}",
                            f"{i.venue_detail.strip("'")}",
                        ]

                        if current not in venues:
                            venues.append(current)

            print(venues)


def venue_csv():
    df = pd.read_csv(
        r"C:\Users\bvw20\Documents\Personal\Databruce Project\venues and detail.csv",
        encoding="utf-8",
    )

    with load_db() as conn:
        cur = conn.cursor()

        for row in df.itertuples():
            count = df["url"].value_counts().get(row.url)

            if count > 1:
                print(row.url, row.name, row.detail)

                # cur.execute(
                #     """UPDATE venues SET detail = %s WHERE brucebase_url = %s""",
                #     (row.detail, row.url),
                # )

    # print(df)


# asyncio.run(main("2024"))
# read_signs()
# parser_scrape()
venue_csv()
