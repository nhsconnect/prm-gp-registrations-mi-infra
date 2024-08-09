from enum import Enum
from io import BytesIO
from zipfile import ZipFile

import requests


class TrudItem(Enum):
    NHS_ODS_WEEKLY = "58"
    ORG_REF_DATA_MONTHLY = "242"


class TrudApiService:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url

    def get_release_list(self, item_number: TrudItem, is_latest=False):
        latest = "?latest" if is_latest else ""
        url_endpoint = (
            self.api_url
            + self.api_key
            + "/items/"
            + item_number.value
            + "/releases"
            + latest
        )
        trud_response = requests.get(url=url_endpoint)
        trud_response.raise_for_status()
        return trud_response.json().get("releases", [])

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
        response = requests.get(url=download_url)
        response.raise_for_status()
        return response.content

    def unzipping_files(self, zip_file, path=None, byte: bool = False):
        myzip = ZipFile(BytesIO(zip_file) if byte else zip_file)
        if path in myzip.namelist():
            return myzip.extract(path)
        return None
