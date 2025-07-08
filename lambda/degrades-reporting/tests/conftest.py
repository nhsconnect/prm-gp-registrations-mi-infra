import boto3
from datetime import datetime
import os
from dataclasses import dataclass
from moto import mock_aws
from tests.mocks.sqs_messages.degrades import (
    MOCK_COMPLEX_DEGRADES_MESSAGE,
    MOCK_FIRST_DEGRADES_MESSAGE,
    MOCK_SIMPLE_DEGRADES_MESSAGE,
)
from degrade_utils.dynamo_service import DynamoService
from degrade_utils.utils import extract_degrades_payload
from models.degrade_message import DegradeMessage
from degrade_utils.s3_service import S3Service

import pytest

MOCK_INTERACTION_ID = "88888888-4444-4444-4444-121212121212"
REGION_NAME = "us-east-1"
MOCK_BUCKET = "test-s3-bucket"
MOCK_DEGRADES_MESSAGE_TABLE_NAME = "degrades_messages_table"
MOCK_DEGRADES_QUEUE_NAME = "degrades_queue"
TEST_DEGRADES_DATE = "2024-09-20"

MOCK_DEGRADES_MESSAGE_TABLE_ATTRIBUTES = [
    {"AttributeName": "Timestamp", "AttributeType": "N"},
    {"AttributeName": "MessageId", "AttributeType": "S"},
]

MOCK_DEGRADES_MESSAGE_TABLE_KEY_SCHEMA = [
    {"AttributeName": "Timestamp", "KeyType": "HASH"},
    {"AttributeName": "MessageId", "KeyType": "RANGE"},
]

def readfile(filename: str) -> str:
    with open(filename, "r") as file:
        file_content = file.read()
    return file_content

@pytest.fixture
def mock_invalid_event_empty_query_string():
    api_gateway_event = {
        "httpMethod": "GET",
        "queryStringParameters": {},
        "headers": {},
    }

    return api_gateway_event


@pytest.fixture
def mock_invalid_event_without_date():
    api_gateway_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"not a date string": "hello"},
        "headers": {},
    }

    return api_gateway_event


@pytest.fixture
def mock_invalid_event_invalid_date_format():
    api_gateway_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"date": "hello"},
        "headers": {},
    }

    return api_gateway_event


@pytest.fixture
def mock_valid_event_valid_date():
    api_gateway_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"date": "2024-01-01"},
        "headers": {},
    }

    return api_gateway_event


@pytest.fixture
def mock_scheduled_event():
    event = {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "2024-09-21T06:00:00Z",
        "region": "us-east-1",
        "resources": ["arn:aws:events:us-east-1:123456789012:rule/ExampleRule"],
        "detail": {},
    }
    return event


@pytest.fixture
def context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        aws_request_id: str = MOCK_INTERACTION_ID
        invoked_function_arn: str = (
            "arn:aws:lambda:eu-west-1:123456789101:function:test"
        )

    return LambdaContext()


@pytest.fixture
def mock_table():
    with mock_aws():
        conn = boto3.resource("dynamodb", region_name=REGION_NAME)
        degrades_table = conn.create_table(
            TableName=MOCK_DEGRADES_MESSAGE_TABLE_NAME,
            KeySchema=MOCK_DEGRADES_MESSAGE_TABLE_KEY_SCHEMA,
            AttributeDefinitions=MOCK_DEGRADES_MESSAGE_TABLE_ATTRIBUTES,
            BillingMode="PAY_PER_REQUEST",
        )
        yield degrades_table


@pytest.fixture
def mock_table_with_files(mock_table):
    with mock_aws():
        degrades_messages = [
            MOCK_COMPLEX_DEGRADES_MESSAGE,
            MOCK_FIRST_DEGRADES_MESSAGE,
            MOCK_SIMPLE_DEGRADES_MESSAGE,
        ]
        degrades = [
            DegradeMessage(
                timestamp=int(
                    datetime.fromisoformat(
                        message["eventGeneratedDateTime"]
                    ).timestamp()
                ),
                message_id=message["eventId"],
                event_type=message["eventType"],
                degrades=extract_degrades_payload(message["payload"]),
            )
            for message in degrades_messages
        ]

        for degrade in degrades:
            DegradeMessage.model_validate(degrade)
            mock_table.put_item(
                Item=degrade.model_dump(by_alias=True, exclude={"event_type"})
            )

    yield mock_table


@pytest.fixture
def mock_s3_with_files():
    with mock_aws():
        folder_path = "tests/mocks/mixed_messages"
        json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

        conn = boto3.resource("s3", region_name=REGION_NAME)
        bucket = conn.create_bucket(Bucket=MOCK_BUCKET)

        for file in json_files:
            bucket.upload_file(os.path.join(folder_path, file), f"2024/01/01/{file}")

        yield bucket


@pytest.fixture
def mock_s3_service(mocker):
    with mock_aws():
        service = S3Service()
        mocker.patch.object(service, "list_files_from_S3")
        mocker.patch.object(service, "get_file_from_S3")
        mocker.patch.object(service, "upload_file")
        yield service
        service._instance = None


@pytest.fixture
def mock_sqs():
    with mock_aws():
        client = boto3.resource("sqs", region_name=REGION_NAME)
        queue = client.create_queue(QueueName=MOCK_DEGRADES_QUEUE_NAME)
        yield queue


@pytest.fixture
def mock_dynamo_service(mocker):
    service = DynamoService()
    mocker.patch.object(service, "query")

    yield service
    service._instance = None


@pytest.fixture
def set_env(monkeypatch):
    monkeypatch.setenv("REGION", REGION_NAME)
    monkeypatch.setenv("REGISTRATIONS_MI_EVENT_BUCKET", MOCK_BUCKET)
    monkeypatch.setenv("DEGRADES_MESSAGE_TABLE", MOCK_DEGRADES_MESSAGE_TABLE_NAME)
    monkeypatch.setenv("DEGRADES_SQS_QUEUE_NAME", MOCK_DEGRADES_QUEUE_NAME)
