import os
import csv
from datetime import datetime, timedelta
from models.degrade_message import DegradeMessage
from degrade_utils.dynamo_service import DynamoService
from degrade_utils.s3_service import S3Service
from degrade_utils.utils import get_degrade_totals_from_degrades
from degrade_utils.enums import CsvHeaders

"""Adhoc script to generate daily report from DynamoDB
    DATE, in format YYYY-MM-DD, to be passed in as an environment variable,
    REGION where the dynamodb table is located must be passed in as an environmental variable,
    populate constants BUCKET and TABLE with the name of registrations mi bucket name and degrades table name"""

BUCKET = ""
TABLE = ""


def generate_degrades_daily_summary_report_from_date(date: str):
    dt = datetime.fromisoformat(date)
    midnight = datetime.combine(dt, datetime.min.time()) + timedelta(hours=1)
    timestamp = int(midnight.timestamp())

    dynamo_service = DynamoService()
    degrades = dynamo_service.query(
        key="Timestamp",
        condition=timestamp,
        table_name=TABLE,
    )

    if not degrades:
        print("No degrades found for timeperiod {}".format(date))
        return

    print("Generating degrades daily report for {}".format(date))

    generate_report_from_dynamo_query(degrades, date)

    base_file_key = "reports/daily"

    print(f"Writing summary report to {base_file_key}")

    s3_service = S3Service()
    s3_service.upload_file(
        file=f"/tmp/{date}.csv",
        bucket_name=BUCKET,
        key=f"{base_file_key}/{date}.csv",
    )


def generate_report_from_dynamo_query(
    degrades_from_table: list[dict], date: str
) -> str | None:
    degrades = [DegradeMessage(**message) for message in degrades_from_table]

    print(f"Getting degrades totals from: {degrades}")
    degrade_totals = get_degrade_totals_from_degrades(degrades)

    if degrade_totals.empty:
        print(f"No degrades found for {date}")
        return

    print(f"Writing degrades report...")

    headers = [CsvHeaders.TYPE, CsvHeaders.REASON, CsvHeaders.COUNT]

    degrade_totals.to_csv(f"/tmp/{date}.csv", header=headers, index=False)


if __name__ == "__main__":
    date = "2024-09-20"
    generate_degrades_daily_summary_report_from_date(date)
