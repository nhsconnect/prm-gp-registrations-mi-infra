import json
import os
import unittest
from json import JSONDecodeError
from unittest.mock import patch, call

from main import _send_events_to_splunk_cloud, lambda_handler, UnableToSendEventToSplunkCloud

TEST_URL = "test_url/some_path"
TEST_TOKEN = "test_token"


class TestMain(unittest.TestCase):
    @patch.dict(os.environ, {"SPLUNK_CLOUD_API_TOKEN": TEST_TOKEN})
    @patch.dict(os.environ, {"SPLUNK_CLOUD_URL": TEST_URL})
    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 200, "data": """{"success": true}"""})())
    @patch('boto3.client')
    def test_uploads_events_to_splunk_cloud(self, boto_mock, mock_PoolManager):
        boto_mock("ssm").get_parameter.side_effect = [{"Parameter": {"Value": TEST_TOKEN}},
                                                      {"Parameter": {"Value": TEST_URL}}]

        event_1 = {"someEvent": "a", "eventId": "123"}
        events_list = '[{"someEvent": "a", "eventId": "123"}]'

        result = _send_events_to_splunk_cloud({"Records": [{"body": events_list}]})

        expected_request = json.dumps({
            "source": "itoc:gp2gp",
            "event": event_1
        })

        mock_PoolManager.assert_called_once_with(method='POST', url=TEST_URL, headers={"Authorization": TEST_TOKEN},
                                                 request_body=expected_request)
        assert result is True

    @patch.dict(os.environ, {"SPLUNK_CLOUD_URL": TEST_URL})
    @patch.dict(os.environ, {"SPLUNK_CLOUD_API_TOKEN": TEST_TOKEN})
    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 200, "data": """{"success": true}"""})())
    @patch('boto3.client')
    def test_uploads_multiple_events_to_splunk_cloud(self, boto_mock, mock_PoolManager):
        boto_mock("ssm").get_parameter.side_effect = [{"Parameter": {"Value": TEST_TOKEN}},
                                                      {"Parameter": {"Value": TEST_URL}}]

        event_1 = {"someEvent": "a", "eventId": "123"}
        event_2 = {"someEvent": "b", "eventId": "456"}
        events_list = '[{"someEvent": "a", "eventId": "123"}, {"someEvent": "b", "eventId": "456"}]'

        result = _send_events_to_splunk_cloud({"Records": [{"body": events_list}]})

        expected_request_1 = json.dumps({
            "source": "itoc:gp2gp",
            "event": event_1
        })

        expected_request_2 = json.dumps({
            "source": "itoc:gp2gp",
            "event": event_2
        })

        assert mock_PoolManager.call_count == 2
        mock_PoolManager.assert_has_calls([call(method='POST', url=TEST_URL, headers={"Authorization": TEST_TOKEN},
                                                request_body=expected_request_1),
                                           call(method='POST', url=TEST_URL, headers={"Authorization": TEST_TOKEN},
                                                request_body=expected_request_2)])

        assert result is True

    @patch.dict(os.environ, {"SPLUNK_CLOUD_URL": TEST_URL})
    @patch.dict(os.environ, {"SPLUNK_CLOUD_API_TOKEN": TEST_TOKEN})
    @patch('boto3.client')
    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 400, "data": """{"success": false}"""})())
    def test_throws_exception_when_invalid_input_for_send_events_to_splunk_cloud(self, mock_boto, mock_request):
        self.assertRaises(JSONDecodeError, _send_events_to_splunk_cloud, {"Records": [{"body": ""}]})

    @patch.dict(os.environ, {"SPLUNK_CLOUD_URL": TEST_URL})
    @patch.dict(os.environ, {"SPLUNK_CLOUD_API_TOKEN": TEST_TOKEN})
    @patch('boto3.client')
    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 400, "data": """{"success": false}"""})())
    def test_returns_false_when_unable_to_upload_event(self, mock_boto, mock_request):
        result = lambda_handler({"Records": [{"body": '[{"someEvent": "a", "eventId": "123"}]'}]}, None)

        assert result is False
