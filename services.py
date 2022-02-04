import os
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator, List, Optional

import requests


def fetch_from_list(shipment_list: List[str]) -> Iterator[requests.Response]:
    """Takes a list of shipment numbers and calls get_data to fetch data from maersk api
    If list consists of one number, fetches synchronously, if list is more than one,
    fetches asynchronously"""
    api = os.environ["MAERSK_API"]
    url_list = tuple(api + shipment for shipment in shipment_list)

    if len(url_list) == 1:
        return [get_data(url_list[0])]

    elif len(url_list) > 1:
        with ThreadPoolExecutor(max_workers=10) as executor:
            return executor.map(get_data, url_list)


def get_data(url: str) -> Optional[requests.request]:
    """Fetches data from Maersk API"""
    try:
        return requests.get(url, timeout=10)
    except requests.exceptions:
        return None
