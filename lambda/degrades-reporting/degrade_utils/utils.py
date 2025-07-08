import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

from models.degrade_message import DegradeMessage, Degrade


def get_key_from_date(date: str):
    return date.replace("-", "/")


def calculate_number_of_degrades(path: str, files: list[str]) -> int:
    total = 0

    for file_name in files:
        file_path = os.path.join(path, file_name)
        with open(file_path, "rb") as json_file:
            data = json.load(json_file)
            eventType = data.get("eventType", None)
            if eventType is not None and eventType == "DEGRADES":
                total += 1
    return total


def is_degrade(file) -> bool:
    data = json.loads(file)
    event_type = data.get("eventType", None)

    return event_type is not None and event_type == "DEGRADES"


def extract_degrades_payload(payload: dict) -> list[Degrade]:
    return [
        Degrade(type=degrade["type"], reason=degrade["reason"])
        for degrade in payload["degrades"]
    ]


def extract_query_timestamp_from_scheduled_event_trigger(
    event: dict,
) -> tuple[int, str] | None:
    event_trigger_time = event.get("time", "")

    if event_trigger_time:
        dt = datetime.fromisoformat(event_trigger_time)
        query_date = dt - timedelta(days=1)
        midnight = datetime.combine(query_date, datetime.min.time())
        return int(midnight.timestamp()), query_date.strftime("%Y-%m-%d")


def get_degrade_totals_from_degrades(degrades_messages: list[DegradeMessage]) -> dict:
    degrade_totals = defaultdict(int)

    for degrade_message in degrades_messages:
        for degrade in degrade_message.degrades:
            degrade_type_reason = f"{degrade.type}: {degrade.reason}"
            degrade_totals[degrade_type_reason] += 1

    total = sum(degrade_totals.values())
    degrade_totals["TOTAL"] += total

    return degrade_totals
