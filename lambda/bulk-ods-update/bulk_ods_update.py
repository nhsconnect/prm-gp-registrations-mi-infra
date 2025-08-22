import csv
from datetime import datetime, timedelta, timezone
import logging
import os
import tempfile
from utils.enums.ods import OdsDownloadType
from utils.models.ods_models import PracticeOds, IcbOds
from utils.services.ods_api_service import OdsApiService
from utils.constants.ods_constants import (
    GP_FILE_HEADERS,
    GP_FILE_NAME,
    GP_REPORT_NAME,
    ICB_FILE_HEADERS,
    ICB_REPORT_NAME,
    ICB_FILE_NAME,
    ODS_API_URL,
    ODS_API_DATE_QUERY
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
TEMP_DIR = tempfile.mkdtemp(dir="/tmp")
seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

def lambda_handler():
    try:
        ods_service = OdsApiService(
            api_url=ODS_API_URL,
        )
        extract_and_process_ods_gp_data(ods_service)
        extract_and_process_ods_icb_data(ods_service)
        return {"statusCode": 200}
    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}")
        return {"statusCode": 400}


def extract_and_process_ods_gp_data(ods_service: OdsApiService):
    logger.info("Extracting and processing ODS GP data")

    download_file = ods_service.get_download_file(
        ods_service.api_url + GP_REPORT_NAME + ODS_API_DATE_QUERY + seven_days_ago
    )
    file_name = os.path.join(TEMP_DIR, GP_FILE_NAME)
    
    with open(file_name, "wb") as f:
        f.write(download_file)

    gp_ods_data = ods_csv_to_dict(file_name, GP_FILE_HEADERS)
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

    logger.info("Proceeding to download ICB data")
    url = ods_service.api_url + ICB_REPORT_NAME + ODS_API_DATE_QUERY + seven_days_ago

    download_file = ods_service.get_download_file(url)
        
    icb_ods_data_amended_data = []
    logger.info("Extracting and processing ODS ICB data")

    file_name = os.path.join(TEMP_DIR, ICB_FILE_NAME)
    with open(file_name, "wb") as f:
        f.write(download_file)
    
    icb_ods_data = ods_csv_to_dict(file_name, ICB_FILE_HEADERS)
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
    
def status_from_close_date(close_date: str | None) -> str:
    return "Closed" if close_date else "Open"

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
                        PracticeOds.practice_status.set(status_from_close_date(amended_record.get("CloseDate"))),
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
                icb.update(actions=[IcbOds.icb_name.set(amended_record.get("IcbName")), IcbOds.icb_status.set(status_from_close_date(amended_record.get("CloseDate")))])
                logger.info(
                    f'Overwriting for ODS: {amended_record.get("IcbOdsCode")} - Name: {amended_record.get("IcbName")}')
            except Exception as e:
                logger.info(f"Failed to create/update record by ICB ODS code: {str(e)}")
