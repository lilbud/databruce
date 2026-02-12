"""Scraper functions.

This module provides:
- get: Make a GET request to the given URL.
- post: Make a POST request to the given URL.
"""

import httpx
from user_agent import generate_user_agent


def get_client() -> httpx.Client:
    """Create a client for requests and return."""
    headers = {
        "User-Agent": generate_user_agent(),
        "Cookie": "wikidot_token7=0",
    }

    return httpx.Client(headers=headers, timeout=30)


def get(url: str, client: httpx.Client) -> httpx.Response | None:
    """Make a GET request to the given URL."""
    try:
        response = client.get(url)
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
        return None
    else:
        return response


def post(category_id: str, client: httpx.Client) -> str | None:
    """Make a POST request to Brucebase's category list for the given category."""
    try:
        response = client.post(
            "http://brucebase.wikidot.com/ajax-module-connector.php",
            data={
                "category_id": category_id,
                "moduleName": "list/WikiCategoriesPageListModule",
                "wikidot_token7": "0",
            },
        )

    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
        return None
    except KeyError as e:
        print(f"Key Not Found in Response Dictionary: {e}")
        return None
    else:
        return response.json()["body"]
