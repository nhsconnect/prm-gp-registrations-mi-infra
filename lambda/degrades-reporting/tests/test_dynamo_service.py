import os
from datetime import datetime

import pytest
from moto import mock_aws
from boto3.dynamodb.conditions import Key
from degrade_utils.utils import extract_degrades_payload
from models.degrade_message import DegradeMessage
from tests.mocks.sqs_messages.degrades import (
    MOCK_COMPLEX_DEGRADES_MESSAGE,
    MOCK_FIRST_DEGRADES_MESSAGE,
    MOCK_SIMPLE_DEGRADES_MESSAGE,
)

from tests.mocks.dynamo_response.degrade_table import simple_message_timestamp

from degrade_utils.dynamo_service import DynamoService

degrades_messages = [
    MOCK_COMPLEX_DEGRADES_MESSAGE,
    MOCK_FIRST_DEGRADES_MESSAGE,
    MOCK_SIMPLE_DEGRADES_MESSAGE,
]


@mock_aws
def test_dynamo_service_queries_table(mock_table, set_env):
    degrades_messages = [
        MOCK_COMPLEX_DEGRADES_MESSAGE,
        MOCK_FIRST_DEGRADES_MESSAGE,
        MOCK_SIMPLE_DEGRADES_MESSAGE,
    ]
    degrades = [
        DegradeMessage(
            timestamp=int(
                datetime.fromisoformat(message["eventGeneratedDateTime"]).timestamp()
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

    service = DynamoService()
    actual = service.query(
        "Timestamp", simple_message_timestamp, os.getenv("DEGRADES_MESSAGE_TABLE")
    )
    expected = mock_table.query(
        KeyConditionExpression=Key("Timestamp").eq(simple_message_timestamp)
    )["Items"]

    assert actual == expected


@mock_aws
def test_dynamo_service_query_raises_error_client_error(set_env, caplog):
    expected_message = "There has been an error:"
    with pytest.raises(Exception):
        service = DynamoService()
        service.query("Timestamp", simple_message_timestamp, "table_does_not_exist")
        assert expected_message in caplog.records[-1].msg
