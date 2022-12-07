import json
import os
import unittest
from unittest.mock import patch, MagicMock
from main import _upload_events_to_s3, _extract_events_from_sqs_messages, _generate_s3_key


class TestMain(unittest.TestCase):
    @patch('boto3.client')
    @patch.dict(os.environ, {"MI_EVENTS_OUTPUT_S3_BUCKET_NAME": "test_bucket_name"})
    def test_should_upload_events_to_s3(self, mock_boto_client):
        events = '[{"eventId": "event_id_1", "registrationEventDateTime": "2000-01-02T09:10:00Z", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}]'
        message_of_event = json.dumps({"Message":events})
        lambda_input = {"Records": [{"body": message_of_event}]}
        expected_event = '{"eventId": "event_id_1", "registrationEventDateTime": "2000-01-02T09:10:00Z", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}'

        put_spy = MagicMock()
        mock_boto_client("s3").put_object = put_spy
        result = _upload_events_to_s3(lambda_input)
        assert result is True
        expected_path = "2000/01/02/09/event_id_1.json"
        put_spy.assert_called_once_with(Bucket="test_bucket_name", Key=expected_path, Body=expected_event)

    def test_extracting_events_from_sqs_messages(self):
        events = '[{"eventId": "event_id_1", "registrationEventDateTime": "2000-01-02T09:10:00Z", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}]'
        message_of_event = json.dumps({"Message":events})
        lambda_input = {"Records": [{"body": message_of_event}]}

        extracted_event = _extract_events_from_sqs_messages(lambda_input)

        event = {"eventId": "event_id_1", "registrationEventDateTime": "2000-01-02T09:10:00Z", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}
        assert extracted_event == [event]

    def test_generate_s3_key(self):
        event = {"eventId": "event_id_1", "registrationEventDateTime": "2000-01-02T09:10:00Z", "eventType":
        "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}

        expected_key = "2000/01/02/09/event_id_1.json"
        result = _generate_s3_key(event)

        assert result == expected_key
