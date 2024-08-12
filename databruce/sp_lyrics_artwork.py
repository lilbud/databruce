import asyncio
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup as bs4
from tools.scraping import scraper

boot = Path(
    r"E:\Media\Music\Bootlegs\Bruce Springsteen\_tosort\randolph\2005\2005-04-22   PARAMOUNT THEATRE (CC)\Artwork",
)


async def main(id: str) -> None:
    """."""
    base_url = "https://www.springsteenlyrics.com"

    response = await scraper.get(
        f"https://www.springsteenlyrics.com/bootlegs.php?item={id}",
    )

    try:
        soup = bs4(response.text, "lxml")

        img_links = soup.find_all("a", href=re.compile(r"_artwork_\d+.jpg"))

        for link in img_links:
            filename = link["href"].split("/")[-1]

            download_path = Path(boot, filename)

            if not download_path.exists():
                print(filename, " doesn't exist, downloading")

                try:
                    img = await scraper.get(f"{base_url}/{link["href"]}")

                    if img:
                        Path.open(download_path, "wb").write(img.content)
                        print(filename, " downloaded")

                except httpx.RequestError:
                    print("failed")
            else:
                print(filename, " exists, skipping")
    except httpx.RequestError:
        print("failed")


asyncio.run(main(id="3987"))
