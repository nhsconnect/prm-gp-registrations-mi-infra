import calendar
import csv
import logging
import os
import tempfile
from datetime import date, timedelta, datetime

import boto3

from utils.enums.trud import OdsDownloadType, TrudItem
from utils.models.ods_models import PracticeOds, IcbOds
from utils.services.ssm_service import SsmSecretManager
from utils.services.trud_api_service import TrudApiService
from utils.trud_files import (
    GP_FILE_HEADERS,
    ICB_FILE_HEADERS,
    ICB_MONTHLY_FILE_PATH,
    ICB_QUARTERLY_FILE_PATH,
    ICB_MONTHLY_FILE_NAME,
    ICB_QUARTERLY_FILE_NAME,
    GP_WEEKLY_FILE_NAME,
    GP_WEEKLY_ZIP_FILE_PATH,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TEMP_DIR = tempfile.mkdtemp(dir="/tmp")


def lambda_handler(event, context):
    try:
        ssm = boto3.client("ssm")
        trud_api_key_param = os.environ.get("TRUD_API_KEY_PARAM_NAME")
        ssm_service = SsmSecretManager(ssm)
        trud_api_key = ssm_service.get_secret(trud_api_key_param) if trud_api_key_param else ""
        trud_service = TrudApiService(
            api_key=trud_api_key,
            api_url=os.environ.get("TRUD_FHIR_API_URL_PARAM_NAME"),
        )

        extract_and_process_ods_gp_data(trud_service)
        extract_and_process_ods_icb_data(trud_service)

        return {"statusCode": 200}
    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}")
        return {"statusCode": 400}


def find_date_for_friday(start_date):
    last_friday = start_date
    while last_friday.weekday() != 4:
        last_friday -= timedelta(days=1)
    return last_friday


def determine_if_last_friday_was_the_last_friday_of_the_month():
    logger.info("Determining if last friday date was the last friday of the month")
    today = date.today()
    last_friday = find_date_for_friday(today)

    total_days_in_month = calendar.monthrange(last_friday.year, last_friday.month)[1]
    last_date_of_month = date(last_friday.year, last_friday.month, total_days_in_month)

    last_friday_of_month = find_date_for_friday(last_date_of_month)

    return last_friday == last_friday_of_month


def check_release_date_within_last_7_days(release_date_string: str):
    try:
        release_date = datetime.strptime(release_date_string, '%Y-%m-%d').date()
        today = date.today()
        days_since_release = today - release_date
        return days_since_release <= timedelta(days=7)
    except (TypeError, ValueError):
        logger.info("failed to check release date")
        raise UnableToGetReleaseDate()


def extract_and_process_ods_gp_data(trud_service: TrudApiService):
    logger.info("Extracting and processing ODS GP data")

    gp_ods_releases = trud_service.get_release_list(
        TrudItem.NHS_ODS_WEEKLY, is_latest=True
    )
    gp_ods_latest_releases = gp_ods_releases[0]
    logger.info(gp_ods_releases)

    download_file_bytes = trud_service.get_download_file(
        gp_ods_latest_releases.get("archiveFileUrl")
    )

    eppracur_csv_path = os.path.join(TEMP_DIR, GP_WEEKLY_FILE_NAME)

    epraccur_zip_file = trud_service.unzipping_files(
        download_file_bytes, GP_WEEKLY_ZIP_FILE_PATH, TEMP_DIR, True
    )
    trud_service.unzipping_files(epraccur_zip_file, GP_WEEKLY_FILE_NAME, TEMP_DIR)

    gp_ods_data = trud_csv_to_dict(eppracur_csv_path, GP_FILE_HEADERS)
    gp_ods_data_amended_data = get_amended_records(gp_ods_data)

    if gp_ods_data_amended_data:
        logger.info(
            f"Found {len(gp_ods_data_amended_data)} amended GP data records to update"
        )
        compare_and_overwrite(OdsDownloadType.GP, gp_ods_data_amended_data)
        return

    logger.info("No amended GP data found")


def extract_and_process_ods_icb_data(trud_service: TrudApiService):
    logger.info("Getting latest ICB release details")

    icb_ods_releases = trud_service.get_release_list(
        TrudItem.ORG_REF_DATA_MONTHLY, True
    )
    icb_ods_latest_release = icb_ods_releases[0]
    logger.info(icb_ods_releases)
    try:
        release_date_string = icb_ods_latest_release.get("releaseDate")
        is_latest_icb_download_recent = check_release_date_within_last_7_days(release_date_string)
    except UnableToGetReleaseDate:
        is_latest_icb_download_recent = determine_if_last_friday_was_the_last_friday_of_the_month()

    if not is_latest_icb_download_recent:
        logger.info("No ICB download for this week, skipping download")
        return None

    logger.info("Proceeding to download ICB data")
    is_quarterly_release = icb_ods_latest_release.get("name").endswith(".0.0")
    download_file = trud_service.get_download_file(
        icb_ods_latest_release.get("archiveFileUrl")
    )

    icb_zip_file_path = (
        ICB_MONTHLY_FILE_PATH if not is_quarterly_release else ICB_QUARTERLY_FILE_PATH
    )
    icb_csv_file_name = (
        ICB_MONTHLY_FILE_NAME if not is_quarterly_release else ICB_QUARTERLY_FILE_NAME
    )

    icb_ods_data_amended_data = []
    logger.info("Extracting and processing ODS ICB data")

    if icb_zip_file := trud_service.unzipping_files(
            download_file, icb_zip_file_path, TEMP_DIR, True
    ):
        if icb_csv_file := trud_service.unzipping_files(
                icb_zip_file, icb_csv_file_name, TEMP_DIR
        ):
            icb_ods_data = trud_csv_to_dict(icb_csv_file, ICB_FILE_HEADERS)
            icb_ods_data_amended_data = get_amended_records(icb_ods_data)

    if icb_ods_data_amended_data:
        logger.info(
            f"Found {len(icb_ods_data_amended_data)} amended ICB data records to update"
        )
        compare_and_overwrite(OdsDownloadType.ICB, icb_ods_data_amended_data)
        return

    logger.info("No amended ICB data found")


def get_amended_records(data: list[dict]) -> list[dict]:
    return [
        amended_data
        for amended_data in data
        if amended_data.get("AmendedRecordIndicator") == "1"
    ]


def trud_csv_to_dict(file_path: str, headers: list[str]) -> list[dict]:
    with open(file_path, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_reader.fieldnames = headers
        data_list = []
        for row in csv_reader:
            data_list.append(dict(row))
        return data_list


def compare_and_overwrite(download_type: OdsDownloadType, data: list[dict]):
    if download_type == OdsDownloadType.GP:
        logger.info("Comparing GP Practice data")
        for amended_record in data:
            try:
                practice = PracticeOds(amended_record.get("PracticeOdsCode"))
                practice.update(
                    actions=[
                        PracticeOds.practice_name.set(
                            amended_record.get("PracticeName")
                        ),
                        PracticeOds.icb_ods_code.set(amended_record.get("IcbOdsCode")),
                    ]
                )
                logger.info(
                    f'Overwriting for ODS: {amended_record.get("PracticeOdsCode")} - Name: {amended_record.get("PracticeName")} | ICB: {amended_record.get("IcbOdsCode")}')
            except Exception as e:
                logger.info(
                    f"Failed to create/update record by Practice ODS code: {str(e)}"
                )

    if download_type == OdsDownloadType.ICB:
        logger.info("Comparing ICB data")
        for amended_record in data:
            try:
                icb = IcbOds(amended_record.get("IcbOdsCode"))
                icb.update(actions=[IcbOds.icb_name.set(amended_record.get("IcbName"))])
                logger.info(
                    f'Overwriting for ODS: {amended_record.get("IcbOdsCode")} - Name: {amended_record.get("IcbName")}')
            except Exception as e:
                logger.info(f"Failed to create/update record by ICB ODS code: {str(e)}")


class UnableToGetReleaseDate(Exception):
    pass
