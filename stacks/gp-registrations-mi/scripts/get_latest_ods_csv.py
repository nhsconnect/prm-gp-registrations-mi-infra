import csv

from services.trud_api_service import TrudApiService, TrudItem

GP_FILE_HEADERS = ['OdsCode','GpName','NG','HLHG','AD1','AD2','AD3','AD4','AD5','PostCode','OD','CD','Null1','Null2','IcbOdsCode','JPD','LPD','CTN','Null3','Null4','Null5','AM','Null6','GOR','Null7','Null8','Null9']
ICB_FILE_HEADERS = ['OdsCode','IcbName','NG','HLHG','AD1','AD2','AD3','AD4','AD5','PostCode','OD','CD','Null1','OSTC','Null2','Null3','Null4','Null5','Null6','Null7','Null8','AM','Null9','Null10','Null11','Null12','Null13']

ICB_MONTHLY_FILE_PATH = 'eamendam.zip'
ICB_QUARTERLY_FILE_PATH = 'ocsissue/data/eccg.zip'

ICB_MONTHLY_FILE_NAME = 'eccgam.csv'
ICB_QUARTERLY_FILE_NAME = 'eccg.csv'
def create_modify_csv(file_path: str, modify_file_path: str, headers_list: list, modify_headers: list):
    with open(file_path, newline='') as original, open(modify_file_path, 'w', newline='') as output:
        reader = csv.DictReader(original, delimiter=',',
                                fieldnames=headers_list)
        writer = csv.DictWriter(output, delimiter=',', fieldnames=modify_headers)
        writer.writeheader()
        writer.writerows({key: row[key] for key in modify_headers} for row in reader)

def get_gp_latest_ods_csv(service):
    release_list_response = service.get_release_list(TrudItem.NHS_ODS_WEEKLY, True)
    download_file = service.get_download_file(release_list_response[0].get('archiveFileUrl'))
    epraccur_zip_file = service.unzipping_files(download_file,'Data/epraccur.zip', True)
    epraccur_csv_file = service.unzipping_files(epraccur_zip_file, 'epraccur.zip')
    create_modify_csv(epraccur_csv_file, 'full_modify_gps_ods.csv', GP_FILE_HEADERS , ['OdsCode', 'GpName', 'IcbOdsCode'])

def get_icb_latest_ods_csv(service):
    release_list_response = service.get_release_list(TrudItem.ORG_REF_DATA_MONTHLY, False)
    download_url_by_release = service.get_download_url_by_release(release_list_response)
    for release, url in download_url_by_release.items():
        download_file = service.get_download_file(url)

        is_quarterly_release = release.endswith('.0.0')
        zip_file_path = ICB_MONTHLY_FILE_PATH if not is_quarterly_release else ICB_QUARTERLY_FILE_PATH
        output_name = 'update_icb' + release if not is_quarterly_release else 'full_icb' + release
        csv_file_name = ICB_MONTHLY_FILE_NAME if not is_quarterly_release else ICB_QUARTERLY_FILE_NAME

        epraccur_zip_file = service.unzipping_files(download_file, zip_file_path, True)
        epraccur_csv_file = service.unzipping_files(epraccur_zip_file, csv_file_name)
        create_modify_csv(epraccur_csv_file, output_name, GP_FILE_HEADERS , ['OdsCode', 'IcbName'])

trud_service = TrudApiService()
get_gp_latest_ods_csv(trud_service)