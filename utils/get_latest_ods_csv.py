import csv
from datetime import date
import sys
import os

from .services.ods_api_service import OdsApiService
from .ods_files import (
    ALL_ICB_AND_GP_FILES,
    ECCGAM_ZIP_URL,
    GP_WEEKLY_REPORT_NAME,
    ICB_MONTHLY_FILE_PATH,
    ICB_MONTHLY_REPORT_NAME,
    ICB_QUARTERLY_FILE_PATH,
    ICB_MONTHLY_FILE_NAME,
    ICB_QUARTERLY_FILE_NAME,
    ICB_FILE_HEADERS,
    GP_FILE_HEADERS,
    GP_WEEKLY_FILE_NAME,
    GP_WEEKLY_ZIP_FILE_PATH,
    ICB_QUARTERLY_REPORT_NAME,
)


def create_modify_csv(
    file_path: str,
    modify_file_path: str,
    headers_list: list,
    modify_headers: list,
    write_to_file: bool,
    additional_rows=None,
):
    with open(file_path, newline="") as original, open(
        f"stacks/gp-registrations-mi/terraform/{modify_file_path}", "w", newline=""
    ) as output:
        reader = csv.DictReader(original, delimiter=",", fieldnames=headers_list)
        csv_modified_rows = [
            {key: row[key] for key in modify_headers} for row in reader
        ]
        if additional_rows and write_to_file:
            csv_modified_rows.extend(additional_rows)
        if write_to_file:
            write_to_csv(output, modify_headers, csv_modified_rows)
            return None
        return csv_modified_rows


def write_to_csv(file_path, headers_list: list, rows_list: list):
    writer = csv.DictWriter(file_path, delimiter=",", fieldnames=headers_list)
    writer.writeheader()
    writer.writerows(rows_list)


def get_gp_latest_ods_csv(service):
    download_file = service.get_download_file(
        os.getenv("ODS_API_URL") + GP_WEEKLY_REPORT_NAME
    )
    epraccur_zip_file = service.unzipping_files(
        download_file, GP_WEEKLY_ZIP_FILE_PATH, byte=True
    )
    epraccur_csv_file = service.unzipping_files(epraccur_zip_file, GP_WEEKLY_FILE_NAME)
    create_modify_csv(
        epraccur_csv_file,
        "initial_full_gps_ods.csv",
        GP_FILE_HEADERS,
        ["PracticeOdsCode", "PracticeName", "IcbOdsCode"],
        True,
    )


def get_icb_latest_ods_csv(service):
    icb_update_changes = []
    for file in ALL_ICB_AND_GP_FILES:
        url = ECCGAM_ZIP_URL if file == ICB_MONTHLY_REPORT_NAME else os.getenv("ODS_API_URL") + file
        download_file = service.get_download_file(url)
        csv_modified_rows = None
        is_quarterly_release = file == ICB_QUARTERLY_REPORT_NAME
        zip_file_path = (
            ICB_MONTHLY_FILE_PATH
            if not is_quarterly_release
            else ICB_QUARTERLY_FILE_PATH
        )
        output_name = (
            "update_icb_" + date.today() + ".csv"
            if not is_quarterly_release
            else "initial_full_icb_ods.csv"
        )
        csv_file_name = (
            ICB_MONTHLY_FILE_NAME
            if not is_quarterly_release
            else ICB_QUARTERLY_FILE_NAME
        )

        if epraccur_zip_file := service.unzipping_files(
            download_file, zip_file_path, byte=True
        ):
            if epraccur_csv_file := service.unzipping_files(
                epraccur_zip_file, csv_file_name
            ):
                csv_modified_rows = create_modify_csv(
                    epraccur_csv_file,
                    output_name,
                    ICB_FILE_HEADERS,
                    ["IcbOdsCode", "IcbName"],
                    is_quarterly_release,
                    icb_update_changes,
                )
        if csv_modified_rows:
            icb_update_changes.extend(csv_modified_rows)


if __name__ == "__main__":
    try:
        ods_service = OdsApiService(sys.argv[1])
        get_gp_latest_ods_csv(ods_service)
        get_icb_latest_ods_csv(ods_service)
        print("\nOds download process complete.")
    except Exception as e:
        print(f"\nExiting Process! {e}")
