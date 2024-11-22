"""File for testing random code/functions/ideas."""

import asyncio
import json
import re
from pathlib import Path

import enchant
import ftfy
import musicbrainzngs
from bs4 import BeautifulSoup as bs4
from database.db import load_db
from dotenv import load_dotenv
from psycopg.rows import dict_row
from spellchecker import SpellChecker
from textblob import TextBlob, Word
from tools.scraping import scraper

load_dotenv()

# from tags.tags import get_tags

musicbrainzngs.set_useragent("Chrome", "37.0.2062.94", contact=None)

# conn = db.load_db()

# geolocator = Nominatim(user_agent="Chrome 37.0.2062.94")

# location = geolocator.geocode("Abidjan		Ivory Coast")

# print(location.raw)
