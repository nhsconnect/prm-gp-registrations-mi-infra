import os
import csv
from datetime import datetime
from models.degrade_message import DegradeMessage
from degrade_utils.dynamo_service import DynamoService
from degrade_utils.s3_service import S3Service
from degrade_utils.utils import get_degrade_totals_from_degrades

"""Adhoc script to generate daily report from DynamoDB
    date to be in format YYYY-MM-DD"""


def generate_degrades_daily_summary_report_from_date(date: str):
    dt = datetime.fromisoformat(date)
    midnight = datetime.combine(dt, datetime.min.time())
    timestamp = int(midnight.timestamp())

    dynamo_service = DynamoService()
    degrades = dynamo_service.query(
        key="Timestamp",
        condition=timestamp,
        table_name=os.getenv("DEGRADES_MESSAGE_TABLE"),
    )

    if not degrades:
        print("No degrades found for timeperiod {}".format(date))
        return

    print("Generating degrades daily report for {}".format(date))

    file_path = generate_report_from_dynamo_query(degrades)

    base_file_key = "/reports/daily"

    print(f"Writing summary report to {base_file_key}")

    s3_service = S3Service()
    s3_service.upload_file(
        file=file_path,
        bucket_name=os.getenv("REGISTRATIONS_MI_EVENT_BUCKET"),
        key=f"{base_file_key}/{date}.csv",
    )


def generate_report_from_dynamo_query(
    degrades_from_table: list[dict], date: str
) -> str:
    degrades = [DegradeMessage(**message) for message in degrades_from_table]

    print(f"Getting degrades totals from: {degrades}")
    degrade_totals = get_degrade_totals_from_degrades(degrades)

    print(f"Writing degrades report...")
    with open(f"{os.getcwd()}/tmp/{date}.csv", "w") as output_file:
        fieldnames = [key for key in degrade_totals.keys()]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for degrade in degrade_totals:
            writer.writerow(degrade)

    return f"{os.getcwd()}/tmp/{date}.csv"


if __name__ == "__main__":
    date = os.getenv("DATE")
    generate_degrades_daily_summary_report_from_date(date)
