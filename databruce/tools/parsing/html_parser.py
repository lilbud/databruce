"""Functions for parsing HTML.

This module provides:
- get_all_links: Get links from page that match a given pattern.
- get_page_title: Return title from given page.
- get_event_date: Return the event date from the given string.
- get_event_day: Get day of week for a provided date.
"""

import re

from bs4 import BeautifulSoup as bs4


async def get_clean_links(soup: bs4, pattern: str) -> list[str]:
    """Get links from a page that match pattern, strip tag from start.

    Many of the tables use the brucebase link as the PK, though with the
    tag stripped from the start (/song:)
    """
    return [
        {"url": re.sub(pattern, "", link["href"]), "text": link.text.strip()}
        for link in soup.find_all("a", href=re.compile(pattern))
    ]


async def get_all_links(soup: bs4, pattern: str) -> list[dict[str, str]]:
    """Get links from a page that match pattern. Keep tag."""
    return [
        {"url": link["href"].strip(), "text": link.text.strip()}
        for link in soup.find_all("a", href=re.compile(pattern))
    ]


async def get_page_title(soup: bs4) -> str:
    """Return title from given page."""
    return soup.find("div", id="page-title").text.strip()


async def get_venue_url(soup: bs4) -> str:
    """Return venue url from given page."""
    return soup.find("a", href=re.compile("/venue:"))["href"].replace("/venue:", "")


async def get_show_descriptor_from_title(title: str) -> str:
    """Return the descriptor in the page title i.e (Early/Late)."""
    try:
        return re.search(r"\((\S+)\)$", title.strip()).group(1)
    except AttributeError:
        return ""


async def get_event_date(event_url: str) -> str:
    """Return the event date from the given string."""
    try:
        return re.search(r"\d{4}-\d{2}-\d{2}", event_url)[0]
    except AttributeError:
        return ""
