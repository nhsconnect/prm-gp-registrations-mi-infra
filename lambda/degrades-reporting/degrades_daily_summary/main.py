import csv
import json
import os
import logging
from models.degrade_message import DegradeMessage
from utils.dynamo_service import DynamoService
from utils.s3_service import S3Service
from utils.utils import (
    extract_query_timestamp_from_scheduled_event_trigger,
    get_degrade_totals_from_degrades,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Retrieving timestamp and date from event")
    query_timestamp, query_day = extract_query_timestamp_from_scheduled_event_trigger(
        event
    )

    logger.info(f"Querying dynamo for degrades with timestamp: {query_timestamp}")
    dynamo_service = DynamoService()
    degrades = dynamo_service.query(
        key="Timestamp",
        condition=query_timestamp,
        table_name=os.getenv("DEGRADES_MESSAGE_TABLE"),
    )

    if not degrades:
        logger.info(f"No degrades found for {query_day}")
        return

    logger.info(f"Generating report for {query_day}")

    file_path = generate_report_from_dynamo_query(degrades, query_day)

    base_file_key = "/reports/daily/"

    logger.info(f"Writing summary report to {base_file_key}")

    s3_service = S3Service()
    s3_service.upload_file(
        file=file_path,
        bucket_name=os.getenv("REGISTRATIONS_MI_EVENT_BUCKET"),
        key=f"{base_file_key}{query_day}.csv",
    )


def generate_report_from_dynamo_query(
    degrades_from_table: list[dict], date: str
) -> str:
    degrades = [DegradeMessage(**message) for message in degrades_from_table]

    logger.info(f"Getting degrades totals from: {degrades}")
    degrade_totals = get_degrade_totals_from_degrades(degrades)

    logger.info(f"Writing degrades report...")
    with open(f"{os.getcwd()}/tmp/reports/{date}.csv", "w+") as output_file:
        fieldnames = [key for key in degrade_totals.keys()]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(degrade_totals)

    return f"{os.getcwd()}/tmp/reports/{date}.csv"
