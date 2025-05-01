"""Functions for parsing HTML."""

import re

from bs4 import BeautifulSoup as bs4


async def strip_tag(url: str) -> str:
    """Remove category tag from start of Brucebase URL."""
    return re.sub("^/.*:", "", url)


async def get_clean_links(soup: bs4, pattern: str) -> list[str]:
    """Get links from a page that match pattern, strip tag from start."""
    return [
        {
            "url": re.sub(pattern, "", link["href"]),
            "text": link.text.strip(),
        }
        for link in soup.find_all("a", href=re.compile(pattern))
    ]


async def get_all_links(soup: bs4, pattern: str) -> list[dict[str, str]]:
    """Get links from a page that match pattern. Keep tag."""
    return [
        {"url": link["href"].strip(), "text": link.text.strip()}
        for link in soup.find_all("a", href=re.compile(pattern))
    ]


async def get_page_title(soup: bs4) -> str | None:
    """Return title from given page."""
    try:
        return soup.find("div", id="page-title").text.strip()
    except AttributeError:
        return None


async def get_venue_url(soup: bs4) -> list[str, str]:
    """Return venue url from given page."""
    try:
        url = soup.find("a", href=re.compile("/venue:"))["href"].replace("/venue:", "")
        name = soup.find("a", href=re.compile("/venue:")).get_text()

    except TypeError:
        return None
    else:
        return [url, name]


async def get_show_descriptor_from_title(title: str) -> str | None:
    """Return the descriptor in the page title i.e (Early/Late)."""
    try:
        return re.search(r"\((.*)\)$", title.strip()).group(1)
    except AttributeError:
        return None


async def get_event_date(event_url: str) -> str | None:
    """Return the event date from the given string."""
    try:
        return re.search(r"\d{4}-\d{2}-\d{2}", event_url)[0]
    except AttributeError:
        return None
