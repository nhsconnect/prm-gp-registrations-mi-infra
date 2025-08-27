import os
import logging
from datetime import datetime, timedelta

from models.degrade_message import DegradeMessage
from degrade_utils.dynamo_service import DynamoService
from degrade_utils.s3_service import S3Service
from degrade_utils.utils import (
    extract_query_timestamp_from_scheduled_event_trigger,
    get_degrade_totals_from_degrades,
    is_monday,
)
from degrade_utils.generate_weekly_reports import generate_weekly_report
from degrade_utils.enums import CsvHeaders

logging.basicConfig(format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    event_trigger_time = event.get("time", "")
    if not event_trigger_time:
        return

    logger.info("Retrieving timestamp and date from event.")
    query_timestamp, query_day = extract_query_timestamp_from_scheduled_event_trigger(
        event_trigger_time
    )

    logger.info(f"Querying dynamo for degrades with timestamp: {query_timestamp}")
    dynamo_service = DynamoService()
    degrades = dynamo_service.query(
        key="Timestamp",
        condition=query_timestamp,
        table_name=os.getenv("DEGRADES_MESSAGE_TABLE"),
    )

    if degrades:
        logger.info(f"Generating report for {query_day}")

        generate_report_from_dynamo_query(degrades, query_day)

        base_file_key = "reports/daily/"

        logger.info(f"Writing summary report to {base_file_key}")

        s3_service = S3Service()
        s3_service.upload_file(
            file=f"/tmp/{query_day}.csv",
            bucket_name=os.getenv("REGISTRATIONS_MI_EVENT_BUCKET"),
            key=f"{base_file_key}{query_day}.csv",
        )

    else:
        logger.info(f"No degrades found for {query_day}")

    if is_monday(event_trigger_time):
        logger.info(f"Today is Monday")
        reporting_start_date = datetime.fromisoformat(event_trigger_time) - timedelta(
            days=7
        )
        str_date = reporting_start_date.strftime("%Y-%m-%d")
        generate_weekly_report(str_date)


def generate_report_from_dynamo_query(degrades_from_table: list[dict], date: str):
    degrades = [DegradeMessage(**message) for message in degrades_from_table]

    logger.info(f"Getting degrades totals from: {degrades}")
    degrade_totals = get_degrade_totals_from_degrades(degrades)

    if degrade_totals.empty:
        logger.info(f"No degrades found for {date}")
        return

    logger.info(f"Writing degrades report...")

    headers = [CsvHeaders.TYPE, CsvHeaders.REASON, CsvHeaders.COUNT]

    degrade_totals.to_csv(f"/tmp/{date}.csv", header=headers, index=False)
