from datetime import datetime

from models.degrade_message import Degrade
from tests.mocks.sqs_messages.degrades import (
    MOCK_SIMPLE_DEGRADES_MESSAGE,
    MOCK_FIRST_DEGRADES_MESSAGE,
    MOCK_COMPLEX_DEGRADES_MESSAGE,
)

simple_message_timestamp = int(
    datetime.fromisoformat(
        MOCK_SIMPLE_DEGRADES_MESSAGE["eventGeneratedDateTime"]
    ).timestamp()
)
first_message_timestamp = int(
    datetime.fromisoformat(
        MOCK_FIRST_DEGRADES_MESSAGE["eventGeneratedDateTime"]
    ).timestamp()
)
complex_message_timestamp = int(
    datetime.fromisoformat(
        MOCK_COMPLEX_DEGRADES_MESSAGE["eventGeneratedDateTime"]
    ).timestamp()
)

FIRST_DEGRADES_MESSAGE_DYNAMO_RESPONSE = {
    "MessageId": "01-DEGRADES-01",
    "Timestamp": first_message_timestamp,
    "Degrades": [{"Type": "MEDICATION", "Reason": "CODE"}],
}

SIMPLE_DEGRADES_MESSAGE_DYNAMO_RESPONSE = {
    "MessageId": "05-DEGRADES-05",
    "Timestamp": simple_message_timestamp,
    "Degrades": [{"Type": "MEDICATION", "Reason": "CODE"}],
}

COMPLEX_DEGRADES_MESSAGE_DYNAMO_RESPONSE = {
    "MessageId": "02-DEGRADES-02",
    "Timestamp": complex_message_timestamp,
    "Degrades": [
        {"Type": "MEDICATION", "Reason": "CODE"},
        {"Type": "RECORD_ENTRY", "Reason": "CODE"},
        {"Type": "NON_DRUG_ALLERGY", "Reason": "CODE"},
    ],
}
