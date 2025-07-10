import os
import pytest
from scripts.populate_table import populate_degrades_table
from tests.conftest import MOCK_BUCKET, REGION_NAME, MOCK_DEGRADES_QUEUE_NAME
from moto import mock_aws
import boto3
from degrade_utils.utils import calculate_number_of_degrades

test_date = "2024/01/01"


@pytest.fixture()
def mock_s3(mocker):
    return mocker.patch("boto3.client")


def test_populate_table_script_lists_files_from_S3(set_env, mock_s3, mock_s3_service):
    populate_degrades_table(test_date)
    mock_s3_service.list_files_from_S3.assert_called()


@mock_aws
def test_populate_table_script_gets_all_files_from_S3(
    set_env, mock_s3_with_files, mock_sqs, mock_s3_service
):
    mock_s3_service.list_files_from_S3.return_value = ["2024/01/01/01-DEGRADES-01.json"]
    mock_s3_service.read_file_from_S3.return_value = '{"eventType": "DEGRADES"}'
    populate_degrades_table(test_date)
    mock_s3_service.read_file_from_S3.assert_called()


@mock_aws
def test_populate_table_script_send_file_to_sqs(set_env):
    folder_path = "tests/mocks/mixed_messages"
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    conn = boto3.resource("s3", region_name=REGION_NAME)
    bucket = conn.create_bucket(Bucket=MOCK_BUCKET)
    sqs = boto3.client("sqs", region_name="us-east-1")
    sqs.create_queue(QueueName=MOCK_DEGRADES_QUEUE_NAME)
    queue_url = sqs.get_queue_url(QueueName=MOCK_DEGRADES_QUEUE_NAME)["QueueUrl"]

    for file in json_files:
        bucket.upload_file(os.path.join(folder_path, file), f"2024/01/01/{file}")

    populate_degrades_table(test_date)
    number_of_degrade_messages = calculate_number_of_degrades(
        path=folder_path, files=json_files
    )

    messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)[
        "Messages"
    ]
    assert len(messages) == number_of_degrade_messages
