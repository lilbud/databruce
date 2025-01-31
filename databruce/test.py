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
