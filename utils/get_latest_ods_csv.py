import csv
import os
import tempfile
from typing import Any, Callable, Dict, Optional
from services.ods_api_service import OdsApiService
from constants.ods_constants import (
    GP_REPORT_NAME,
    GP_FILE_NAME,
    ICB_FILE_NAME,
    ICB_FILE_HEADERS,
    GP_FILE_HEADERS,
    ICB_REPORT_NAME,
    ODS_API_URL,
)

TEMP_DIR = tempfile.mkdtemp(dir="/tmp")

def create_modify_csv(
    file_path: str,
    modify_file_path: str,
    headers_list: list,
    modify_headers: list,
    write_to_file: bool,
    additional_rows=None,
    derived_columns: Optional[Dict[str, Callable[[dict], Any]]] = None,
):
    derived_columns = derived_columns or {}

    with open(file_path, newline="") as original, open(
        f"stacks/gp-registrations-mi/terraform/{modify_file_path}", "w", newline=""
    ) as output:
        reader = csv.DictReader(original, delimiter=",", fieldnames=headers_list)
        csv_modified_rows = []
        for row in reader:
            out = {}
            for key in modify_headers:
                if key in derived_columns:
                    out[key] = derived_columns[key](row)
                else:
                    out[key] = row.get(key, "")
            csv_modified_rows.append(out)
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

def status_from_close_date(row: dict) -> str:
    close_date = (row.get("CloseDate") or "").strip()
    return "Closed" if close_date else "Open"

def get_gp_latest_ods_csv(service):
    url = service.api_url + GP_REPORT_NAME
    download_file = service.get_download_file(url)
    output_name = "initial_full_gps_ods.csv"
    file_path = os.path.join(TEMP_DIR, GP_FILE_NAME)
    with open(file_path, "wb") as f:
        f.write(download_file)
    create_modify_csv(
        file_path=file_path,
        modify_file_path=output_name,
        headers_list=GP_FILE_HEADERS,
        modify_headers=["PracticeOdsCode", "PracticeName", "IcbOdsCode", "PracticeStatus"],
        write_to_file=True,
        derived_columns={
            "PracticeStatus": status_from_close_date
        },
    )

def get_icb_latest_ods_csv(service):
    url = service.api_url + ICB_REPORT_NAME
    download_file = service.get_download_file(url)
    output_name = "initial_full_icb_ods.csv"
    file_path = os.path.join(TEMP_DIR, ICB_FILE_NAME)
    with open(file_path, "wb") as f:
        f.write(download_file)
    create_modify_csv(
        file_path,
        output_name,
        ICB_FILE_HEADERS,
        ["IcbOdsCode", "IcbName", "IcbStatus"],
        True,
        derived_columns={
            "IcbStatus": status_from_close_date
        },
    )

if __name__ == "__main__":
    try:
        ods_service = OdsApiService(ODS_API_URL)
        get_gp_latest_ods_csv(ods_service)
        get_icb_latest_ods_csv(ods_service)
        print("\nOds download process complete.")
    except Exception as e:
        print(f"\nExiting Process! {e}")
