import re
from typing import List

from shipment import Shipment


def parse_request_text(request: str) -> List[str]:
    """Finds container and transport document numbers in a string and return a list of
    unique numbers"""
    pattern = r"[A-Za-z]{3}U[0-9]{7}|[a-zA-Z0-9]{9}"
    unique_list = []

    for shipment in re.findall(pattern, request.upper()):
        if shipment not in unique_list:
            unique_list.append(shipment)

    return unique_list


def text_for_shipment(shipment: Shipment) -> str:
    """Take dataclass Shipments and creates a text for response"""
    general_text = (
        (f"<b>TD:</b> {shipment.td}\n" if shipment.td else "")
        + (
            f"<b>From:</b> {shipment.pol_city}, {shipment.pol_country}\n"
            if shipment.pol_city and shipment.pol_country
            else ""
        )
        + (
            f"<b>To:</b> {shipment.pod_city}, {shipment.pod_country}"
            if shipment.pod_city and shipment.pod_country
            else ""
        )
    ).rstrip()
    containers_text = "\n\n".join(
        (
            f"<b>{cont.number}</b> - {cont.size} {cont.type}\n"
            + (f"<b>ETA:</b> {cont.eta}\n" if cont.eta else "")
            + (
                f"<b>Last Event:</b> {cont.latest_act} - {cont.latest_city}, "
                f"{cont.latest_country} - {cont.latest_date}"
                if all(
                    (
                        cont.latest_act,
                        cont.latest_city,
                        cont.latest_country,
                        cont.latest_date,
                    )
                )
                else ""
            )
        ).rstrip()
        for cont in shipment.containers
    )
    return general_text + "\n\n" + containers_text


def report_text(request: str, response: str, username: str) -> str:
    """Creates text for a report to send to admin"""
    return (
        f"[REPORT]\n"
        f"Username: {username}\n\n"
        f"Request:\n{request}\n\n"
        f"Response:\n{response}"
    )
