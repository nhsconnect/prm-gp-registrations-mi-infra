import json
import pytest
from datetime import datetime
from degrades_message_receiver.main import lambda_handler
from tests.mocks.dynamo_response.degrade_table import (
    SIMPLE_DEGRADES_MESSAGE_DYNAMO_RESPONSE,
    FIRST_DEGRADES_MESSAGE_DYNAMO_RESPONSE,
    COMPLEX_DEGRADES_MESSAGE_DYNAMO_RESPONSE,
)
from tests.mocks.sqs_messages.degrades import (
    MOCK_COMPLEX_DEGRADES_MESSAGE,
    MOCK_FIRST_DEGRADES_MESSAGE,
    MOCK_SIMPLE_DEGRADES_MESSAGE,
)
from tests.mocks.sqs_messages.document_response import DOCUMENT_RESPONSE


def test_degrades_message_receiver_handles_single_degrade_message(
    set_env, context, mock_table
):
    event = {"Records": [{"body": json.dumps(MOCK_FIRST_DEGRADES_MESSAGE)}]}
    timestamp = int(
        datetime.fromisoformat(
            MOCK_FIRST_DEGRADES_MESSAGE["eventGeneratedDateTime"]
        ).timestamp()
    )

    lambda_handler(event, context)
    response = mock_table.get_item(
        Key={
            "Timestamp": timestamp,
            "MessageId": MOCK_FIRST_DEGRADES_MESSAGE["eventId"],
        }
    )

    expected = FIRST_DEGRADES_MESSAGE_DYNAMO_RESPONSE
    actual = response["Item"]

    assert actual == expected


def test_degrades_message_receiver_handles_more_than_one_degrade_message(
    set_env, context, mock_table
):
    event = {
        "Records": [
            {"body": json.dumps(MOCK_SIMPLE_DEGRADES_MESSAGE)},
            {"body": json.dumps(MOCK_FIRST_DEGRADES_MESSAGE)},
        ]
    }

    lambda_handler(event, context)
    response = mock_table.scan()

    assert len(response["Items"]) == 2
    expected = [
        FIRST_DEGRADES_MESSAGE_DYNAMO_RESPONSE,
        SIMPLE_DEGRADES_MESSAGE_DYNAMO_RESPONSE,
    ]

    actual = [response["Items"][0], response["Items"][1]]

    assert actual == expected


def test_degrades_message_receiver_throws_error_message_not_degrades(
    set_env, context, mock_table, caplog
):
    event = {"Records": [{"body": json.dumps(DOCUMENT_RESPONSE)}]}
    expected_message = "Invalid degrade message"

    with pytest.raises(ValueError):
        lambda_handler(event, context)
        assert expected_message in caplog.records[-1].msg


def test_degrades_message_receiver_handles_simple_degrade_message_payload(
    set_env, context, mock_table
):
    event = {"Records": [{"body": json.dumps(MOCK_SIMPLE_DEGRADES_MESSAGE)}]}
    timestamp = int(
        datetime.fromisoformat(
            MOCK_SIMPLE_DEGRADES_MESSAGE["eventGeneratedDateTime"]
        ).timestamp()
    )

    lambda_handler(event, context)
    response = mock_table.get_item(
        Key={
            "Timestamp": timestamp,
            "MessageId": MOCK_SIMPLE_DEGRADES_MESSAGE["eventId"],
        }
    )

    expected = SIMPLE_DEGRADES_MESSAGE_DYNAMO_RESPONSE
    actual = response["Item"]

    assert actual == expected


def test_degrades_message_receiver_handles_complex_degrade_message_payload(
    set_env, context, mock_table
):
    event = {"Records": [{"body": json.dumps(MOCK_COMPLEX_DEGRADES_MESSAGE)}]}
    timestamp = int(
        datetime.fromisoformat(
            MOCK_COMPLEX_DEGRADES_MESSAGE["eventGeneratedDateTime"]
        ).timestamp()
    )

    lambda_handler(event, context)
    response = mock_table.get_item(
        Key={
            "Timestamp": timestamp,
            "MessageId": MOCK_COMPLEX_DEGRADES_MESSAGE["eventId"],
        }
    )

    expected = COMPLEX_DEGRADES_MESSAGE_DYNAMO_RESPONSE
    actual = response["Item"]

    assert actual == expected
