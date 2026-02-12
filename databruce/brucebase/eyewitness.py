import json
import re
import sys
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup as bs4
from user_agent import generate_user_agent

parent_folder = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_folder))

from tools.scraping import scraper


def get_new_reports():
    headers = {
        "User-Agent": generate_user_agent(),
        "Cookie": "wikidot_token7=0",
    }

    with httpx.Client(headers=headers) as client:
        category_id = 38261438

        response = client.post(
            "http://brucebase.wikidot.com/ajax-module-connector.php",
            data={
                "page": "1",
                "perpage": "200",
                "pageId": "65311375",
                "categoryId": category_id,
                "options": '{"new":true}',
                "moduleName": "changes/SiteChangesListModule",
                "callbackIndex": "7",
                "wikidot_token7": "0",
            },
        )

        # res = scraper.post(category_id="38261438", client=client)

        if response:
            print(response.json().keys())
            # soup = bs4(response.json()["body"], "lxml")

            # for item in soup.find_all("div", {"class": "changes-list-item"}):
            #     print(item.prettify())


# print(parent_folder)
get_new_reports()
