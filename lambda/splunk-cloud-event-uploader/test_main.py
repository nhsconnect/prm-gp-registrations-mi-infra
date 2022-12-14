import json
import os
import unittest
from unittest.mock import patch, call

from main import _send_events_to_splunk_cloud, lambda_handler, UnableToSendEventToSplunkCloud, \
    _extract_events_from_sqs_messages

TEST_URL = "test_url/some_path"
TEST_TOKEN = "test_token"


class TestMain(unittest.TestCase):
    @patch.dict(os.environ, {"SPLUNK_CLOUD_URL": TEST_URL})
    @patch.dict(os.environ, {"SPLUNK_CLOUD_API_TOKEN": TEST_TOKEN})
    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 200, "data": """{"success": true}"""})())
    @patch('boto3.client')
    def test_uploads_multiple_events_to_splunk_cloud_with_lambda_handler(self, boto_mock, mock_PoolManager):
        boto_mock("ssm").get_parameter.side_effect = [{"Parameter": {"Value": TEST_TOKEN}},
                                                      {"Parameter": {"Value": TEST_URL}}]

        events_1 = '[{"someEvent": "a", "eventId": "123"}, {"someEvent": "b", "eventId": "456"}]'
        events_2 = '[{"someEvent": "c", "eventId": "321"}, {"someEvent": "d", "eventId": "654"}]'

        message_of_event_1 = json.dumps({"Message": events_1})
        message_of_event_2 = json.dumps({"Message": events_2})
        lambda_input = {"Records": [{"body": message_of_event_1}, {"body": message_of_event_2}]}

        result = lambda_handler(lambda_input, None)

        expected_request_1 = json.dumps({
            "source": "itoc:gp2gp",
            "event": {"someEvent": "a", "eventId": "123"}
        })

        expected_request_2 = json.dumps({
            "source": "itoc:gp2gp",
            "event": {"someEvent": "b", "eventId": "456"}
        })

        expected_request_3 = json.dumps({
            "source": "itoc:gp2gp",
            "event": {"someEvent": "c", "eventId": "321"}
        })

        expected_request_4 = json.dumps({
            "source": "itoc:gp2gp",
            "event": {"someEvent": "d", "eventId": "654"}
        })

        assert mock_PoolManager.call_count == 4
        mock_PoolManager.assert_has_calls([call(method='POST', url=TEST_URL, headers={"Authorization": TEST_TOKEN},
                                                body=expected_request_1),
                                           call(method='POST', url=TEST_URL, headers={"Authorization": TEST_TOKEN},
                                                body=expected_request_2),
                                           call(method='POST', url=TEST_URL, headers={"Authorization": TEST_TOKEN},
                                                body=expected_request_3),
                                           call(method='POST', url=TEST_URL, headers={"Authorization": TEST_TOKEN},
                                                body=expected_request_4)])

        assert result is True

    @patch.dict(os.environ, {"SPLUNK_CLOUD_API_TOKEN": TEST_TOKEN})
    @patch.dict(os.environ, {"SPLUNK_CLOUD_URL": TEST_URL})
    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 200, "data": """{"success": true}"""})())
    @patch('boto3.client')
    def test_sends_events_to_splunk_cloud(self, boto_mock, mock_PoolManager):
        boto_mock("ssm").get_parameter.side_effect = [{"Parameter": {"Value": TEST_TOKEN}},
                                                      {"Parameter": {"Value": TEST_URL}}]

        events_list = [{"someEvent": "a", "eventId": "123"}, {"someEvent": "b", "eventId": "456"}]

        result = _send_events_to_splunk_cloud(events_list)

        expected_request_1 = json.dumps({
            "source": "itoc:gp2gp",
            "event": {"someEvent": "a", "eventId": "123"}
        })

        expected_request_2 = json.dumps({
            "source": "itoc:gp2gp",
            "event": {"someEvent": "b", "eventId": "456"}
        })

        mock_PoolManager.assert_has_calls([call(method='POST', url=TEST_URL, headers={"Authorization": TEST_TOKEN},
                                                body=expected_request_1),
                                           call(method='POST', url=TEST_URL, headers={"Authorization": TEST_TOKEN},
                                                body=expected_request_2)])
        assert result is True

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

    @patch.dict(os.environ, {"SPLUNK_CLOUD_URL": TEST_URL})
    @patch.dict(os.environ, {"SPLUNK_CLOUD_API_TOKEN": TEST_TOKEN})
    @patch('boto3.client')
    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 400, "data": """{"success": false}"""})())
    def test_throws_exception_when_invalid_input_for_send_events_to_splunk_cloud(self, mock_boto, mock_request):
        self.assertRaises(UnableToSendEventToSplunkCloud, _send_events_to_splunk_cloud, {"Records": [{"body": ""}]})

    @patch.dict(os.environ, {"SPLUNK_CLOUD_URL": TEST_URL})
    @patch.dict(os.environ, {"SPLUNK_CLOUD_API_TOKEN": TEST_TOKEN})
    @patch('boto3.client')
    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 400, "data": """{"success": false}"""})())
    def test_returns_false_when_unable_to_upload_event(self, mock_boto, mock_request):
        events = '[{"eventId": "event_id_1", "eventGeneratedDateTime": "2000-01-02T09:10:00", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}]'
        message_of_event = json.dumps({"Message": events})
        lambda_input = {"Records": [{"body": message_of_event}]}

        self.assertRaises(Exception, lambda_handler, lambda_input)
