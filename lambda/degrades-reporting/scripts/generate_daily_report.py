import os
import csv
from datetime import datetime
from models.degrade_message import DegradeMessage
from degrade_utils.dynamo_service import DynamoService
from degrade_utils.s3_service import S3Service
from degrade_utils.utils import get_degrade_totals_from_degrades

"""Adhoc script to generate daily report from DynamoDB
    DATE, in format YYYY-MM-DD, to be passed in as an environment variable,
    REGION where the dynamodb table is located must be passed in as an environmental variable,
    populate constants BUCKET and TABLE with the name of registrations mi bucket name and degrades table name"""

BUCKET = os.getenv("REGISTRATIONS_MI_EVENT_BUCKET")
TABLE = os.getenv("DEGRADES_MESSAGE_TABLE")


def generate_degrades_daily_summary_report_from_date(date: str):
    dt = datetime.fromisoformat(date)
    midnight = datetime.combine(dt, datetime.min.time())
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

    file_path = generate_report_from_dynamo_query(degrades, date)

    base_file_key = "reports/daily"

    print(f"Writing summary report to {base_file_key}")

    s3_service = S3Service()
    s3_service.upload_file(
        file=file_path,
        bucket_name=BUCKET,
        key=f"{base_file_key}/{date}.csv",
    )


def generate_report_from_dynamo_query(
    degrades_from_table: list[dict], date: str
) -> str:
    degrades = [DegradeMessage(**message) for message in degrades_from_table]

    print(f"Getting degrades totals from: {degrades}")
    degrade_totals = get_degrade_totals_from_degrades(degrades)

    print(f"Writing degrades report...")

    headers = ["Type", "Reason", "Count"]

    with open(f"/tmp/{date}.csv", "w") as output_file:
        fieldnames = headers
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for degrade in degrade_totals:
            writer.writerow(degrade)


    return f"/tmp/{date}.csv"

def split_degrade_type_reason(degrade_type_reason):
    type_reason = degrade_type_reason.split(":")
    return type_reason[0], type_reason[1]


if __name__ == "__main__":
    date = os.getenv("DATE")
    generate_degrades_daily_summary_report_from_date(date)
