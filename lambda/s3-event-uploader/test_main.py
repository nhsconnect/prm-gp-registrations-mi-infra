import os
import unittest
from unittest.mock import patch, MagicMock
from main import _upload_events_to_s3, _extract_events_from_sqs_messages


class TestMain(unittest.TestCase):
    @patch('boto3.client')
    @patch.dict(os.environ, {"MI_EVENTS_OUTPUT_S3_BUCKET_NAME": "test_bucket_name"})
    def test_should_upload_events_to_s3(self, mock_boto_client):
        event = """{"eventId": "event_id_1", "registrationEventDateTime": "2000-01-02T09:10:00Z" "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}"""
        lambda_input = {"Records": [{"body": {"Message": [event]}}]}

        put_spy = MagicMock()
        mock_boto_client("s3").put_object = put_spy
        result = _upload_events_to_s3(lambda_input)
        assert result is True
        expected_path = "2000/01/02/09/event_id_1.json"
        put_spy.assert_called_once_with(Bucket="test_bucket_name", Key=expected_path, Body=event)

    def test_extracting_events_from_sqs_messages(self):
        lambda_input = {"Records": [{"body": {"Message": [{"eventId": "event_id_1",
                                                           "registrationEventDateTime": "2000-01-02T09:10:00Z",
                                                           "eventType": "REGISTRATIONS",
                                                           "requestingPracticeOdsCode": "ODS_1",
                                                           "sendingPracticeOdsCode": "ODS_1"}]}}]}
        print(lambda_input)
        extracted_event = _extract_events_from_sqs_messages(lambda_input)

        event = {"eventId": "event_id_1", "registrationEventDateTime": "2000-01-02T09:10:00Z",
                 "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}
        print(extracted_event)
        print([event])
        assert extracted_event == [event]
