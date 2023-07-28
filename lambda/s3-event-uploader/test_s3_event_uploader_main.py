import json
import os
import unittest
from unittest.mock import patch, MagicMock, call

from s3_event_uploader_main import _upload_events_to_s3, _extract_events_from_sqs_messages, _generate_s3_key, UnableToUploadEventToS3


class TestS3EventUploaderMain(unittest.TestCase):
    @patch('boto3.client')
    @patch.dict(os.environ, {"MI_EVENTS_OUTPUT_S3_BUCKET_NAME": "test_bucket_name"})
    def test_should_upload_events_to_s3(self, mock_boto_client):
        events_1 = '[{"eventId": "event_id_1", "eventGeneratedDateTime": "2000-01-02T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}, {"eventId": "event_id_2", "eventGeneratedDateTime": "2000-01-03T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_2", "sendingPracticeOdsCode": "ODS_2"}]'
        events_2 = '[{"eventId": "event_id_3", "eventGeneratedDateTime": "2000-01-02T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_3", "sendingPracticeOdsCode": "ODS_3"}, {"eventId": "event_id_4", "eventGeneratedDateTime": "2000-01-03T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_4", "sendingPracticeOdsCode": "ODS_4"}]'
        message_of_event_1 = json.dumps({"Message": events_1})
        message_of_event_2 = json.dumps({"Message": events_2})
        lambda_input = {"Records": [{"body": message_of_event_1}, {"body": message_of_event_2}]}
        expected_event_1 = '{"eventId": "event_id_1", "eventGeneratedDateTime": "2000-01-02T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}'
        expected_event_2 = '{"eventId": "event_id_2", "eventGeneratedDateTime": "2000-01-03T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_2", "sendingPracticeOdsCode": "ODS_2"}'
        expected_event_3 = '{"eventId": "event_id_3", "eventGeneratedDateTime": "2000-01-02T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_3", "sendingPracticeOdsCode": "ODS_3"}'
        expected_event_4 = '{"eventId": "event_id_4", "eventGeneratedDateTime": "2000-01-03T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_4", "sendingPracticeOdsCode": "ODS_4"}'

        put_spy = MagicMock()
        mock_boto_client("s3").put_object = put_spy
        result = _upload_events_to_s3(lambda_input)
        assert result is True
        expected_path_1 = "2000/01/02/event_id_1.json"
        expected_path_2 = "2000/01/03/event_id_2.json"
        expected_path_3 = "2000/01/02/event_id_3.json"
        expected_path_4 = "2000/01/03/event_id_4.json"
        put_spy.assert_has_calls([call(Bucket="test_bucket_name", Key=expected_path_1, Body=expected_event_1),
                                  call(Bucket="test_bucket_name", Key=expected_path_2, Body=expected_event_2),
                                  call(Bucket="test_bucket_name", Key=expected_path_3, Body=expected_event_3),
                                  call(Bucket="test_bucket_name", Key=expected_path_4, Body=expected_event_4)])

    def test_extracting_events_from_sqs_messages(self):
        events_1 = '[{"eventId": "event_id_1", "eventGeneratedDateTime": "2000-01-02T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}, {"eventId": "event_id_2", "eventGeneratedDateTime": "2000-01-03T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_2", "sendingPracticeOdsCode": "ODS_2"}]'
        events_2 = '[{"eventId": "event_id_3", "eventGeneratedDateTime": "2000-01-02T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_3", "sendingPracticeOdsCode": "ODS_3"}, {"eventId": "event_id_4", "eventGeneratedDateTime": "2000-01-03T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_4", "sendingPracticeOdsCode": "ODS_4"}]'
        message_of_event_1 = json.dumps({"Message": events_1})
        message_of_event_2 = json.dumps({"Message": events_2})
        lambda_input = {"Records": [{"body": message_of_event_1}, {"body": message_of_event_2}]}

        extracted_event = _extract_events_from_sqs_messages(lambda_input)
        expected_events = [
            {"eventId": "event_id_1", "eventGeneratedDateTime": "2000-01-02T09:10:00", "eventType": "REGISTRATIONS",
             "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"},
            {"eventId": "event_id_2", "eventGeneratedDateTime": "2000-01-03T09:10:00", "eventType": "REGISTRATIONS",
             "requestingPracticeOdsCode": "ODS_2", "sendingPracticeOdsCode": "ODS_2"},
            {"eventId": "event_id_3", "eventGeneratedDateTime": "2000-01-02T09:10:00", "eventType": "REGISTRATIONS",
             "requestingPracticeOdsCode": "ODS_3", "sendingPracticeOdsCode": "ODS_3"},
            {"eventId": "event_id_4", "eventGeneratedDateTime": "2000-01-03T09:10:00", "eventType": "REGISTRATIONS",
             "requestingPracticeOdsCode": "ODS_4", "sendingPracticeOdsCode": "ODS_4"}]

        assert extracted_event == expected_events

    def test_generate_s3_key(self):
        event = {"eventId": "event_id_1", "eventGeneratedDateTime": "2000-01-02T09:10:00", "eventType":
            "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}

        expected_key = "2000/01/02/event_id_1.json"
        result = _generate_s3_key(event)

        assert result == expected_key

    @patch('boto3.client')
    def test_throws_exception_when_invalid_input_for_upload_events_to_s3(self, mock_boto):
        put_spy = MagicMock()
        mock_boto("s3").put_object = put_spy
        event = '[{"incorrect event":"format"}]'
        message_of_event = json.dumps({"Message": event})
        self.assertRaises(UnableToUploadEventToS3, _upload_events_to_s3, {"Records": [{"body": message_of_event}]})
