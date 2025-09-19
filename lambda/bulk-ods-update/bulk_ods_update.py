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
FULL_BACKFILL = os.getenv("ODS_FULL_BACKFILL_FLAG", False)
DEBUG_LOG_RETURN = os.getenv("ODS_DEBUG", False)
TEMP_DIR = tempfile.mkdtemp(dir="/tmp")
seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

def lambda_handler(event, context):
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
    url = (ods_service.api_url + GP_REPORT_NAME
            if FULL_BACKFILL
            else ods_service.api_url + GP_REPORT_NAME + ODS_API_DATE_QUERY + seven_days_ago)

    download_file = ods_service.get_download_file(url)
    file_name = os.path.join(TEMP_DIR, GP_FILE_NAME)
    
    with open(file_name, "wb") as f:
        f.write(download_file)

    gp_ods_data = ods_csv_to_dict(file_name, GP_FILE_HEADERS)
    gp_ods_data_amended_data = gp_ods_data if FULL_BACKFILL else get_amended_records(gp_ods_data)

    if gp_ods_data_amended_data:
        logger.info(f"GP records to update: {len(gp_ods_data_amended_data)} (full_backfill={FULL_BACKFILL})")

        compare_and_overwrite(OdsDownloadType.GP, gp_ods_data_amended_data)
        return

    logger.info("No amended GP data found")


def extract_and_process_ods_icb_data(ods_service: OdsApiService):
    logger.info("Getting latest ICB release details")
    url = (ods_service.api_url + ICB_REPORT_NAME
            if FULL_BACKFILL
            else ods_service.api_url + ICB_REPORT_NAME + ODS_API_DATE_QUERY + seven_days_ago)

    download_file = ods_service.get_download_file(url)
    file_name = os.path.join(TEMP_DIR, ICB_FILE_NAME)
    with open(file_name, "wb") as f:
        f.write(download_file)

    icb_ods_data = ods_csv_to_dict(file_name, ICB_FILE_HEADERS)
    icb_ods_data_amended_data = icb_ods_data if FULL_BACKFILL else get_amended_records(icb_ods_data)

    if icb_ods_data_amended_data:
        logger.info(f"ICB records to update: {len(icb_ods_data_amended_data)} (full_backfill={FULL_BACKFILL})")
        compare_and_overwrite(OdsDownloadType.ICB, icb_ods_data_amended_data)
    else:
        logger.info("No ICB data to update")


def get_amended_records(data: list[dict]) -> list[dict]:
    return [
        amended_data
        for amended_data in data
        if amended_data.get("AmendedRecordIndicator") == "1"
    ]
    
def status_from_close_date(close_date: str | None) -> str:
    return "Inactive" if close_date else "Active"

def ods_csv_to_dict(file_path: str, headers: list[str]) -> list[dict]:
    with open(file_path, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_reader.fieldnames = headers
        data_list = []
        for row in csv_reader:
            data_list.append(dict(row))
        return data_list

def update_gp_data(amended_record: dict):
    try:
        odsCode = amended_record.get("PracticeOdsCode")
        practice = PracticeOds(odsCode)
        practice.update(actions=[
            PracticeOds.practice_name.set(amended_record.get("PracticeName")), 
            PracticeOds.practice_status.set(status_from_close_date(amended_record.get("CloseDate"))),
            PracticeOds.last_updated.set(datetime.now(timezone.utc))
            ])

        if DEBUG_LOG_RETURN:
            practice.refresh() 
            logger.info(f"Updated Practice {odsCode}: {practice.attribute_values}")
    except Exception as e:
        logger.info(f"Failed to create/update record by Practice ODS code: {str(e)}")
        
def update_icb_data(amended_record: dict):
    try:
        odsCode = amended_record.get("IcbOdsCode")
        icb = IcbOds(odsCode)
        icb.update(actions=[
            IcbOds.icb_name.set(amended_record.get("IcbName")), 
            IcbOds.icb_status.set(status_from_close_date(amended_record.get("CloseDate"))),
            IcbOds.last_updated.set(datetime.now(timezone.utc))
            ])

        if DEBUG_LOG_RETURN:
            icb.refresh() 
            logger.info(f"Updated ICB {odsCode}: {icb.attribute_values}")
    except Exception as e:
        logger.info(f"Failed to create/update record by ICB ODS code: {str(e)}")
        
def compare_and_overwrite(download_type: OdsDownloadType, data: list[dict]):
    if download_type == OdsDownloadType.GP:
        logger.info("Comparing GP Practice data")
        for amended_record in data:
            update_gp_data(amended_record)

    if download_type == OdsDownloadType.ICB:
        logger.info("Comparing ICB data")
        for amended_record in data:
            update_icb_data(amended_record)