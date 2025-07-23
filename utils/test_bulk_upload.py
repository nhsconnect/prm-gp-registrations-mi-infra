import calendar
import csv
import logging
import os
import tempfile
from datetime import date, timedelta, datetime
import boto3
from dotenv import load_dotenv
from enums.ods import OdsDownloadType, OdsItem
from models.ods_models import PracticeOds, IcbOds
from services.ods_api_service import OdsApiService
from ods_files import (
    ECCGAM_ZIP_URL,
    OLD_GP_FILE_HEADERS,
    GP_WEEKLY_FILE_NAME,
    GP_WEEKLY_REPORT_NAME,
    OLD_ICB_FILE_HEADERS,
    ICB_MONTHLY_REPORT_NAME,
    ICB_MONTHLY_FILE_NAME,
    ICB_MONTHLY_FILE_PATH,
    ICB_QUARTERLY_REPORT_NAME,
    ICB_QUARTERLY_FILE_NAME
)

load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TEMP_DIR = tempfile.mkdtemp(dir="/tmp")
ODS_API_URL = "https://www.odsdatasearchandexport.nhs.uk/api/getReport?report="  # Replace with actual ODS API URL

def lambda_handler():
    try:
        ods_service = OdsApiService(
            api_url=ODS_API_URL,
        )

        #extract_and_process_ods_gp_data(ods_service)
        extract_and_process_ods_icb_data(ods_service)

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
        # raise UnableToGetReleaseDate()


def extract_and_process_ods_gp_data(ods_service: OdsApiService):
    logger.info("Extracting and processing ODS GP data")

    download_file = ods_service.get_download_file(
        ods_service.api_url + GP_WEEKLY_REPORT_NAME
    )
    file_name = os.path.join(TEMP_DIR, GP_WEEKLY_FILE_NAME)
    
    with open(file_name, "wb") as f:
        f.write(download_file)

    gp_ods_data = ods_csv_to_dict(file_name, OLD_GP_FILE_HEADERS)
    gp_ods_data_amended_data = get_amended_records(gp_ods_data)

    if gp_ods_data_amended_data:
        logger.info(
            f"Found {len(gp_ods_data_amended_data)} amended GP data records to update"
        )
        compare_and_overwrite(OdsDownloadType.GP, gp_ods_data_amended_data)
        return

    logger.info("No amended GP data found")


def extract_and_process_ods_icb_data(ods_service: OdsApiService):
    logger.info("Getting latest ICB release details")
    icb_report_names = [
        ICB_MONTHLY_REPORT_NAME,
        ICB_QUARTERLY_REPORT_NAME,
    ]
    for report in icb_report_names:
        logger.info("Proceeding to download ICB data")
        is_quarterly_release = report == ICB_QUARTERLY_REPORT_NAME
        url = ECCGAM_ZIP_URL if report == ICB_MONTHLY_REPORT_NAME else ods_service.api_url + report

        download_file = ods_service.get_download_file(url)
            
        icb_ods_data_amended_data = []
        logger.info("Extracting and processing ODS ICB data")

        if is_quarterly_release:
            file_name = os.path.join(TEMP_DIR, ICB_QUARTERLY_FILE_NAME)
            with open(file_name, "wb") as f:
                f.write(download_file)
            
            icb_ods_data = ods_csv_to_dict(file_name, OLD_ICB_FILE_HEADERS)
            icb_ods_data_amended_data = get_amended_records(icb_ods_data)
        else:
            file_name = os.path.join(TEMP_DIR, ICB_MONTHLY_FILE_PATH)
            with open(file_name, "wb") as f:
                f.write(download_file)
                
            if icb_csv_file := ods_service.unzipping_files(
                file_name, ICB_MONTHLY_FILE_NAME, TEMP_DIR
            ):
                icb_ods_data = ods_csv_to_dict(icb_csv_file, OLD_ICB_FILE_HEADERS)
                icb_ods_data_amended_data = get_amended_records(icb_ods_data)
            else:
                logger.warning("Failed to unzip ICB monthly CSV from archive")
                return

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


def ods_csv_to_dict(file_path: str, headers: list[str]) -> list[dict]:
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


# class UnableToGetReleaseDate(Exception):
#     pass

lambda_handler()