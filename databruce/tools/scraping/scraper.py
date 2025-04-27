"""Scraper functions.

This module provides:
- get: Make a GET request to the given URL.
- post: Make a POST request to the given URL.
"""

import httpx
from user_agent import generate_user_agent


async def get_client() -> httpx.AsyncClient:
    """Create a client for requests and return."""
    headers = {
        "User-Agent": generate_user_agent(),
        "Cookie": "wikidot_token7=0",
    }

    return httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30)


async def get(url: str, client: httpx.AsyncClient) -> httpx.Response:
    """Make a GET request to the given URL."""
    try:
        response = await client.get(url)
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
    else:
        return response


async def post(category_id: str, client: httpx.AsyncClient) -> dict:
    """Make a POST request to Brucebase's category list for the given category."""
    try:
        response = await client.post(
            "http://brucebase.wikidot.com/ajax-module-connector.php",
            data={
                "category_id": category_id,
                "moduleName": "list/WikiCategoriesPageListModule",
                "wikidot_token7": "0",
            },
        )

    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
    except KeyError as e:
        print(f"Key Not Found in Response Dictionary: {e}")
    else:
        return response.json()["body"]
