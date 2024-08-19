import json
import os
from io import BytesIO
from zipfile import ZipFile
import urllib3
from urllib3.util.retry import Retry

import logging

from utils.enums.trud import TrudItem

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TrudApiService:
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url

        retry_strategy = Retry(
            total=3, backoff_factor=1, status_forcelist=[400, 404, 500, 502, 503, 504]
        )

        self.http = urllib3.PoolManager(retries=retry_strategy)

    def get_release_list(self, item_number: TrudItem, is_latest=False):
        latest = "?latest" if is_latest else ""
        url_endpoint = (
            self.api_url + self.api_key + "/items/" + item_number + "/releases" + latest
        )

        try:
            trud_response = self.http.request("GET", url_endpoint)
            trud_data = json.loads(trud_response.data.decode())
            response = trud_data.get("releases", [])
            trud_response.release_conn()

            return response
        except Exception as e:
            logger.info(f"An unexpected error occurred: {e}")
            raise e

    def get_download_url_by_release(
        self, releases_list, break_at_quarterly_release=True
    ):
        download_url_by_release = {}
        for release in releases_list:
            download_url_by_release[release["name"]] = release.get("archiveFileUrl")
            if break_at_quarterly_release and release["name"].endswith(".0.0"):
                break
        return download_url_by_release

    def get_download_file(self, download_url):
        try:
            download_response = self.http.request("GET", download_url)
            logger.info(download_response)
            return download_response.data
        except Exception as e:
            logger.info(f"An unexpected error occurred: {e}")
            raise e

    def unzipping_files(self, zip_file, path=None, path_to_extract=None, byte: bool = False):
        myzip = ZipFile(BytesIO(zip_file) if byte else zip_file)
        if path_to_extract is None:
            path_to_extract = os.getcwd()
        if path in myzip.namelist():
            return myzip.extract(path, path_to_extract)
        return None
