import pytest
from moto import mock_aws
import os
from botocore.exceptions import ClientError
from utils.s3_service import S3Service
from tests.conftest import REGION_NAME, MOCK_BUCKET


@mock_aws
def test_service_list_files_from_S3(set_env, mock_s3_with_files):
    folder_path = "./tests/mocks/mixed_messages"
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    service = S3Service()

    files = service.list_files_from_S3(MOCK_BUCKET, "2024/01/01/")

    assert len(files) == len(json_files)
    for index in range(len(files)):
        assert f"2024/01/01/{json_files[index]}" in files


@mock_aws
def test_list_files_from_S3_raises_error_client_issue(set_env):
    service = S3Service()
    with pytest.raises(ClientError):
        service.list_files_from_S3("test", "2024/01/01/")


@mock_aws
def test_get_file_from_S3(set_env, mock_s3_with_files):
    service = S3Service()
    files_names = service.list_files_from_S3(
        bucket_name=MOCK_BUCKET, prefix="2024/01/01/"
    )

    actual = service.get_file_from_S3(bucket_name=MOCK_BUCKET, key=files_names[0])
    with open("./tests/mocks/mixed_messages/01-DEGRADES-01.json", "rb") as expected:
        assert expected.read() == actual


@mock_aws
def test_get_file_from_S3_raises_error_client_issue(set_env):
    service = S3Service()

    with pytest.raises(ClientError):
        service.get_file_from_S3("test", "key")


@mock_aws
def test_s3_service_uploads_files(set_env, mock_s3_with_files):
    service = S3Service()

    service.upload_file(
        file="./tests/reports/2024-09-20.csv",
        bucket_name=MOCK_BUCKET,
        key="2024/09/20/summary.csv",
    )

    actual = service.get_file_from_S3(MOCK_BUCKET, "2024/09/20/summary.csv")
    with open("./tests/reports/2024-09-20.csv", "rb") as expected:
        assert expected.read() == actual
