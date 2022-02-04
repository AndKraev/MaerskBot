from dataclasses import dataclass
from typing import Union

import requests


@dataclass
class Shipment:
    """Dataclass to store shipment's data"""

    td: str
    pol_city: str
    pol_country: str
    pod_city: str
    pod_country: str
    containers: tuple


@dataclass
class Container:
    """Dataclass to store container's data"""

    number: str
    size: str
    type: str
    eta: str
    latest_act: str
    latest_city: str
    latest_country: str
    latest_date: str


def parse_response(response: requests.Response) -> Union[Shipment, str]:
    """Takes a response from api, checks status code and returns Shipment class or a
    string with error message"""
    if response.status_code == 200:
        return shipment_from_dict(response.json())

    elif response.status_code == 404:
        return "No container shipment found"

    elif response.status_code == 400:
        return "Incorrect search ID"

    else:
        return "Something went wrong"


def shipment_from_dict(datadict: dict) -> Shipment:
    """Creates Shipment dataclass from dict received from maersk API"""
    return Shipment(
        td=datadict.get("tpdoc_num") if "tpdoc_num" in datadict else None,
        pol_city=datadict["origin"].get("city") if "origin" in datadict else None,
        pol_country=datadict["origin"].get("country") if "origin" in datadict else None,
        pod_city=(
            datadict["destination"].get("city") if "destination" in datadict else None
        ),
        pod_country=(
            datadict["destination"].get("country")
            if "destination" in datadict
            else None
        ),
        containers=tuple(
            container_from_dict(cont) for cont in datadict.get("containers")
        ),
    )


def container_from_dict(datadict: dict) -> Container:
    """Creates Container dataclass from dict received from maersk API"""
    return Container(
        number=datadict.get("container_num"),
        size=datadict.get("container_size"),
        type=datadict.get("container_type"),
        eta=datadict.get("eta_final_delivery"),
        latest_act=datadict["latest"].get("activity") if "latest" in datadict else None,
        latest_city=datadict["latest"].get("city") if "latest" in datadict else None,
        latest_country=(
            datadict["latest"].get("country") if "latest" in datadict else None
        ),
        latest_date=(
            convert_datetime(datadict["latest"].get("actual_time"))
            if "latest" in datadict
            else None
        ),
    )


def convert_datetime(date_and_time: str) -> str:
    """Converts data and time received from maersk APO to a format 'date, time'"""
    return ", ".join(date_and_time[:-4].split("T", 1))
