"""Scraper functions.

This module provides:
- get: Make a GET request to the given URL.
- post: Make a POST request to the given URL.
"""

import secrets
from pathlib import Path

import httpx


async def get_random_user_agent() -> str:
    """Return a random user-agent string from the 'user-agents.txt' file.

    'user-agents.txt' is from https://github.com/sushil-rgb/AmazonBuddy
    """
    with Path.open(Path(Path(__file__).parent, "user-agents.txt")) as user_agents:
        return secrets.choice(user_agents.read().splitlines())


async def get(url: str) -> httpx.Response:
    """Make a GET request to the given URL."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                headers={
                    "User-Agent": await get_random_user_agent(),
                    "Cookie": "wikidot_token7=0",
                },
                follow_redirects=True,
                timeout=5,
            )
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
        else:
            return response


async def post(category_id: str) -> dict:
    """Make a POST request to Brucebase's category list for the given category."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://brucebase.wikidot.com/ajax-module-connector.php",
                headers={
                    "User-Agent": await get_random_user_agent(),
                    "Cookie": "wikidot_token7=0",
                },
                data={
                    "category_id": category_id,
                    "moduleName": "list/WikiCategoriesPageListModule",
                    "wikidot_token7": "0",
                },
            )

            return response.json()["body"]
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
        except KeyError as e:
            print(f"Key Not Found in Response Dictionary: {e}")
