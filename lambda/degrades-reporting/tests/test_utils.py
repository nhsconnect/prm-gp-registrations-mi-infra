import os

from models.degrade_message import DegradeMessage, Degrade
from tests.conftest import TEST_DEGRADES_DATE
from tests.mocks.dynamo_response.degrade_table import (
    simple_message_timestamp,
    FIRST_DEGRADES_MESSAGE_DYNAMO_RESPONSE,
    SIMPLE_DEGRADES_MESSAGE_DYNAMO_RESPONSE,
    COMPLEX_DEGRADES_MESSAGE_DYNAMO_RESPONSE,
)
from tests.mocks.sqs_messages.degrades import (
    MOCK_FIRST_DEGRADES_MESSAGE,
    MOCK_COMPLEX_DEGRADES_MESSAGE,
)
from degrade_utils.utils import (
    get_key_from_date,
    calculate_number_of_degrades,
    is_degrade,
    extract_degrades_payload,
    extract_query_timestamp_from_scheduled_event_trigger,
    get_degrade_totals_from_degrades,
)


def test_get_key_from_date():
    date = "2020-01-01"
    assert get_key_from_date(date) == "2020/01/01"


def test_calculate_number_of_degrades():
    folder_path = "tests/mocks/mixed_messages"
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    result = calculate_number_of_degrades(path=folder_path, files=json_files)
    assert result == 5


def test_is_degrade_with_degrade_message():
    with open("tests/mocks/mixed_messages/01-DEGRADES-01.json", "r") as file:
        assert is_degrade(file.read())


def test_is_degrade_with_file_not_degrades_message():
    with open("tests/mocks/mixed_messages/01-DOCUMENT_RESPONSES-01.json", "r") as file:
        assert is_degrade(file.read()) == False


def test_extract_degrades_payload_simple_message():
    payload = MOCK_FIRST_DEGRADES_MESSAGE["payload"]

    actual = extract_degrades_payload(payload)
    expected = [Degrade(type="MEDICATION", reason="CODE")]
    assert actual == expected


def test_extract_degrades_payload_complex_message():
    payload = MOCK_COMPLEX_DEGRADES_MESSAGE["payload"]

    actual = extract_degrades_payload(payload)
    expected = [
        Degrade(type="MEDICATION", reason="CODE"),
        Degrade(type="RECORD_ENTRY", reason="CODE"),
        Degrade(type="NON_DRUG_ALLERGY", reason="CODE"),
    ]
    assert actual == expected


def test_extract_query_timestamp_from_scheduled_event_trigger(mock_scheduled_event):
    actual = extract_query_timestamp_from_scheduled_event_trigger(mock_scheduled_event)
    expected = (simple_message_timestamp, TEST_DEGRADES_DATE)

    assert actual == expected


def test_get_degrade_totals_from_degrades():
    degrades = [
        DegradeMessage.model_validate(FIRST_DEGRADES_MESSAGE_DYNAMO_RESPONSE),
        DegradeMessage.model_validate(SIMPLE_DEGRADES_MESSAGE_DYNAMO_RESPONSE),
        DegradeMessage.model_validate(COMPLEX_DEGRADES_MESSAGE_DYNAMO_RESPONSE),
    ]
    expected = {"MEDICATION: CODE": 3, "RECORD_ENTRY: CODE": 1, "NON_DRUG_ALLERGY: CODE": 1, "TOTAL": 5}

    actual = get_degrade_totals_from_degrades(degrades)

    assert actual == expected
