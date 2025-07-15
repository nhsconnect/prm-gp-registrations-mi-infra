import json
import os
import pandas as pd
from datetime import datetime, timedelta

from degrade_utils.enums import CsvHeaders
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
    trigger_time: str,
) -> tuple[int, str] | None:

    dt = datetime.fromisoformat(trigger_time)
    query_date = dt - timedelta(days=1)
    midnight = datetime.combine(query_date, datetime.min.time())
    return int(midnight.timestamp()), query_date.strftime("%Y-%m-%d")


def get_degrade_totals_from_degrades(
    degrades_messages: list[DegradeMessage],
) -> pd.DataFrame:

        degrades = []

        for degrade_message in degrades_messages:
            for degrade in degrade_message.degrades:
                degrades.append({CsvHeaders.TYPE: degrade.type, CsvHeaders.REASON: degrade.reason})

        if degrades:
            df = pd.DataFrame(degrades)
            result = df.groupby([CsvHeaders.TYPE, CsvHeaders.REASON]).size().reset_index(name=CsvHeaders.COUNT)
            return result
        else:
            return pd.DataFrame()


def is_monday(date):
    day = datetime.fromisoformat(date)
    return day.weekday() == 0