"""File for testing random code/functions/ideas."""

import asyncio
import json
import re
from pathlib import Path

import enchant
import ftfy
from bs4 import BeautifulSoup as bs4
from database.db import load_db
from dotenv import load_dotenv
from psycopg.rows import dict_row
from spellchecker import SpellChecker
from textblob import TextBlob, Word
from tools.scraping import scraper

load_dotenv()

# from tags.tags import get_tags

# musicbrainzngs.set_useragent("Chrome", "37.0.2062.94", contact=None)

# conn = db.load_db()

# geolocator = Nominatim(user_agent="Chrome 37.0.2062.94")

# location = geolocator.geocode("Abidjan		Ivory Coast")

# print(location.raw)


async def main():
    res = await scraper.get(
        "https://www.filefactory.com/share/fo:c3705fa242d4a8c5,fo:4c2aba2f5ac3fc9f,fo:960344f7e8742151,fo:274bd157db1fe3b3,fo:3e2add03add61beb,fo:0c02d542c7d87ad3,fo:e95729649e789439,fo:34a6eb21436e23d0,fo:62eaa8606dc7ef83,fo:51df2f441f1d63f3,fo:c766224894b65665,fo:363a356614c685af,fo:95cd7820d0e4194a,fo:70966df79b81d402,fo:7fc34af02227dc60,fo:a739582684bd1051,fo:e472d11ba97c1757,fo:3c6224dac30c0c35,fo:9a61db5fde407169,fo:1bb1b1bd53a1c976,fo:343b91efee5dc609,fo:3e8f7acceeec8f4c,fo:b1347f89ca4092be,fo:01e59c2294e214a7,fo:b70d9244c74b1a47,fo:1af3ae4371a5218f,fo:2c4da34acc6bdf95,fo:a42c85e238d635b8,fo:88f2b3cfe3d3cfdd,fo:ba372155c372af23",
    )

    if res:
        soup = bs4(res, "lxml")
        for i in soup.find_all("a", href=re.compile("filefactory.com/folder")):
            link = f"{re.search("http.*/", i["href"])[0]}?export=1"
            text = i.get_text().strip()

            print(f"{text},{link}")


asyncio.run(main())
