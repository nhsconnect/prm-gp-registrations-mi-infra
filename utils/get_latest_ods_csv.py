import csv
import sys
import os
import tempfile
from .services.ods_api_service import OdsApiService
from .ods_files import (
    GP_REPORT_NAME,
    GP_FILE_NAME,
    ICB_FILE_NAME,
    ICB_FILE_HEADERS,
    GP_FILE_HEADERS
)

TEMP_DIR = tempfile.mkdtemp(dir="/tmp")

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
        os.getenv("ODS_API_URL") + GP_REPORT_NAME
    )
    output_name = "initial_full_gps_ods.csv"
    
    file_path = os.path.join(TEMP_DIR, GP_FILE_NAME)
    with open(file_path, "wb") as f:
        f.write(download_file)

    create_modify_csv(
        file_path,
        output_name,
        GP_FILE_HEADERS,
        ["PracticeOdsCode", "PracticeName", "IcbOdsCode"],
        True,
    )


def get_icb_latest_ods_csv(service):
    icb_update_changes = []
    url = service.api_url + ICB_FILE_NAME
    download_file = service.get_download_file(url)
    csv_modified_rows = None

    output_name = "initial_full_icb_ods.csv"
    
    file_path = os.path.join(TEMP_DIR, ICB_FILE_NAME)
    with open(file_path, "wb") as f:
        f.write(download_file)

    csv_modified_rows = create_modify_csv(
        file_path,
        output_name,
        ICB_FILE_HEADERS,
        ["IcbOdsCode", "IcbName"],
        True,
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
