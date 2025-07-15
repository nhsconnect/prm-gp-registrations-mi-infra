import csv
import os
import logging
from models.degrade_message import DegradeMessage
from degrade_utils.dynamo_service import DynamoService
from degrade_utils.s3_service import S3Service
from degrade_utils.utils import (
    extract_query_timestamp_from_scheduled_event_trigger,
    get_degrade_totals_from_degrades,
)
from degrade_utils.enums import CsvHeaders

logging.basicConfig(format="%(levelname)s: %(message)s")
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

    base_file_key = "reports/daily/"

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

    if degrade_totals.empty:
        logger.info(f"No degrades found for {date}")
        return

    logger.info(f"Writing degrades report...")

    headers = [CsvHeaders.TYPE, CsvHeaders.REASON, CsvHeaders.COUNT]

    degrade_totals.to_csv(f"/tmp/{date}.csv", header=headers, index=False)
    # with open(f"/tmp/{date}.csv", "w") as output_file:
    #     fieldnames = headers
    #     writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    #     writer.writeheader()
    #     for degrade in degrade_totals:
    #         writer.writerow(degrade)
    #
    # return f"/tmp/{date}.csv"