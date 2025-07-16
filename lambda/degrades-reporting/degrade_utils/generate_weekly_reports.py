import csv
import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from degrade_utils.s3_service import S3Service
from degrade_utils.enums import CsvHeaders

logging.basicConfig(format="%(levelname)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def generate_weekly_report(date_beginning: str):
    logger.info(f"Getting file keys for reports week beginning: {date_beginning}")
    file_keys = get_keys_from_date_range(date_beginning)

    logger.info(f"Generating weekly summary for week beginning: {date_beginning}")

    weekly_summary = generate_weekly_summary(file_keys, date_beginning)
    new_rows = generate_new_rows_from_week_summary(weekly_summary, date_beginning)

    if not new_rows:
        logger.info(f"No new entries found for week beginning: {date_beginning}")
        return

    s3_service = S3Service()

    try:
        s3_service.download_file(
            bucket_name=os.getenv("REGISTRATIONS_MI_EVENT_BUCKET"),
            key="reports/degrades_weekly_report.csv",
            file="/tmp/degrades_weekly_report.csv",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            logger.info("No weekly summary report found, creating new one")
            with open(
                "/tmp/degrades_weekly_report.csv", "a+"
            ) as updated_weekly_report_csv:
                writer = csv.DictWriter(
                    updated_weekly_report_csv, CsvHeaders.list_values()
                )
                writer.writeheader()

        if e.response["Error"]["Code"] == "404":
            logger.info("No weekly summary report found, creating new one")
            with open(
                "/tmp/degrades_weekly_report.csv", "a+"
            ) as updated_weekly_report_csv:
                writer = csv.DictWriter(
                    updated_weekly_report_csv, CsvHeaders.list_values()
                )
                writer.writeheader()
        else:
            raise e

    with open("/tmp/degrades_weekly_report.csv", "a+") as updated_weekly_report_csv:
        writer = csv.DictWriter(updated_weekly_report_csv, CsvHeaders.list_values())
        writer.writerows(new_rows)

    s3_service.upload_file(
        bucket_name=os.getenv("REGISTRATIONS_MI_EVENT_BUCKET"),
        key="reports/degrades_weekly_report.csv",
        file="/tmp/degrades_weekly_report.csv",
    )

    logger.info(
        f"Successfully updated weekly summary report with summary for week beginning: {date_beginning}"
    )


def get_keys_from_date_range(date_beginning: str) -> list[str]:
    start_date = datetime.fromisoformat(date_beginning)
    week_range = [
        datetime.strftime(start_date + timedelta(days=i), "%Y-%m-%d")
        for i in range(0, 7, 1)
    ]

    return week_range


def generate_weekly_summary(files: list[str], date_beginning) -> dict:
    s3_service = S3Service()
    dfs = []
    logger.info(
        f"Retrieving daily reports for week beginning: {date_beginning} from S3"
    )
    for file in files:
        try:
            csv_body = s3_service.get_object_from_s3(
                bucket_name=os.getenv("REGISTRATIONS_MI_EVENT_BUCKET"),
                key=f"reports/daily/{file}.csv",
            )
            dfs.append(pd.read_csv(csv_body))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.info(f"No daily report found for {file}")
                continue
            else:
                logger.error(e)
                raise e

    if not dfs:
        return {}

    df = pd.concat(dfs).groupby(["Type", "Reason"]).sum()
    week_summary = df.to_dict()
    logger.info(
        f"Successfully generated weekly summary for {date_beginning}: {week_summary}"
    )
    return week_summary


def generate_new_rows_from_week_summary(summary: dict, date_beginning: str) -> list:
    counts = summary.get("Count", {})
    rows = []

    if counts:
        for key, value in counts.items():
            rows.append(
                {
                    CsvHeaders.WEEK_BEGINNING: date_beginning,
                    CsvHeaders.TYPE: key[0],
                    CsvHeaders.REASON: key[1],
                    CsvHeaders.COUNT: value,
                }
            )

    return rows
