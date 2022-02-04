from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import requests


def fetch_from_list(shipment_list):
    url_list = tuple(
        "https://api.maerskline.com/track/" + shipment for shipment in shipment_list
    )

    if len(url_list) == 1:
        return [get_data(url_list[0])]

    elif len(url_list) > 1:
        with ThreadPoolExecutor(max_workers=10) as executor:
            return executor.map(get_data, url_list)


def get_data(url: str) -> Optional[requests.request]:
    try:
        return requests.get(url, timeout=10)
    except requests.exceptions:
        return None
