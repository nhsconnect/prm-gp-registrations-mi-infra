import os
from io import BytesIO
from zipfile import ZipFile
import certifi
import urllib3
from urllib3.exceptions import HTTPError
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class OdsApiService:
    def __init__(self, api_url: str):
        self.api_url = api_url

        retry_strategy = Retry(
            total=3, backoff_factor=1, status_forcelist=[400, 404, 500, 502, 503, 504]
        )

        self.http = urllib3.PoolManager(
            retries=retry_strategy, 
            cert_reqs="CERT_REQUIRED", 
            ca_certs=certifi.where()
            )
        
    def get_download_file(self, download_url):
        try:
            download_response = self.http.request("GET", download_url)
            return download_response.data
        except HTTPError as e:
            logger.info(f"An unexpected error occurred: {e}")

    def unzipping_files(self, zip_file, path=None, path_to_extract=None, byte: bool = False):
        myzip = ZipFile(BytesIO(zip_file) if byte else zip_file)
        if path_to_extract is None:
            path_to_extract = os.getcwd()
        if path in myzip.namelist():
            return myzip.extract(path, path_to_extract)
        return None