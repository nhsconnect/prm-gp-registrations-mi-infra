import os
import unittest
from unittest.mock import patch, MagicMock
from main import _find_icb_ods_code, ICB_ROLE_ID, _fetch_organisation, ODS_PORTAL_URL, EMPTY_ORGANISATION, \
    OdsPortalException, _send_enriched_events_to_sqs_for_uploading, _enrich_events

A_VALID_TEST_ORGANISATION = {
    "Name": "Test Practice",
    "Rels": {
        "Rel": [
            {
                "Status": "Active",
                "Target": {
                    "OrgId": {
                        "extension": "ODS_1"
                    },
                    "PrimaryRoleId": {
                        "id": ICB_ROLE_ID
                    }
                },
            },
        ]
    }
}

class TestMain(unittest.TestCase):
    @patch('boto3.client')
    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 200, "data": """{"Organisation": {"Name": "Test Practice", "Rels": {
        "Rel": [
            {
                "Status": "Active",
                "Target": {
                    "OrgId": {
                        "extension": "ODS_1"
                    },
                    "PrimaryRoleId": {
                        "id": "RO98"
                    }
                }
            }
        ]
    }}}"""})())
    def test_should_enrich_events_with_empty_fields_if_unable_to_fetch_organisation(self, mock_sqs_client,
                                                                                    mock_request):
        events = """{"eventId": "event_id_1", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1"}"""

        sqs_messages = {"Records": [{"body": events}]}

        result = _enrich_events(sqs_messages)

        expected_events = [{"eventId": "event_id_1",
                            "eventType": "REGISTRATIONS",
                            "requestingPracticeOdsCode": "ODS_1",
                            "sendingPracticeOdsCode": "ODS_1",
                            "requestingPracticeName": "Test Practice",
                            "requestingPracticeIcbOdsCode": "ODS_1",
                            "requestingPracticeIcbName": "Test Practice",
                            "sendingPracticeName": "Test Practice",
                            "sendingPracticeIcbOdsCode": "ODS_1",
                            "sendingPracticeIcbName": "Test Practice",
                            }]
        assert result == expected_events

    @patch('boto3.client')
    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 404, "data": A_VALID_TEST_ORGANISATION})())
    def test_should_enrich_events_with_all_fields_from_organisation(self, mock_sqs_client, mock_request):
        events = """{"eventId": "event_id_1", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ods_1", "sendingPracticeOdsCode": "ods_2"}"""

        sqs_messages = {"Records": [{"body": events}]}

        result = _enrich_events(sqs_messages)

        expected_events = [{"eventId": "event_id_1",
                            "eventType": "REGISTRATIONS",
                            "requestingPracticeOdsCode": "ods_1",
                            "requestingPracticeIcbOdsCode": None,
                            "requestingPracticeName": None,
                            "requestingPracticeIcbName": None,
                            "sendingPracticeOdsCode": "ods_2",
                            "sendingPracticeName": None,
                            "sendingPracticeIcbOdsCode": None,
                            "sendingPracticeIcbName": None,
                            }]
        assert result == expected_events

    @patch.dict(os.environ, {"SPLUNK_CLOUD_EVENT_UPLOADER_SQS_QUEUE_URL": "test_url"})
    @patch('boto3.client')
    def test_uploads_events_to_sqs(self, mock_boto):
        enriched_events = [{"someEvent": 1}]
        send_message_spy = MagicMock()
        mock_boto("sqs").send_message = send_message_spy

        _send_enriched_events_to_sqs_for_uploading(enriched_events)

        send_message_spy.assert_called_once_with(QueueUrl='test_url', MessageBody='[{"someEvent": 1}]')

    def test_find_icb_ods_code_returns_none_when_organisation_does_not_have_rels(self):
        organisation = {}
        result = _find_icb_ods_code(organisation)
        assert result is None

    def test_find_icb_ods_code_returns_ods_code_when_active_and_primary_role_id_is_an_icb_role(self):
        an_ods_code = "ODS_1"
        organisation = A_VALID_TEST_ORGANISATION
        result = _find_icb_ods_code(organisation)
        assert result == an_ods_code

    def test_find_icb_ods_code_returns_none_when_primary_role_id_is_not_icb(self):
        organisation = {
            "Name": "Test Pharmacy",
            "Rels": {
                "Rel": [
                    {
                        "Status": "Active",
                        "Target": {
                            "OrgId": {
                                "extension": "QJ2"
                            },
                            "PrimaryRoleId": {
                                "id": "NON_ICB_ROLE_ID"
                            }
                        },
                        "id": "RE4"
                    },
                ]
            }
        }
        result = _find_icb_ods_code(organisation)
        assert result is None

    def test_find_icb_ods_code_returns_none_when_inactive_despite_being_an_icb(self):
        organisation = {
            "Name": "Test Pharmacy",
            "Rels": {
                "Rel": [
                    {
                        "Status": "Inactive",
                        "Target": {
                            "OrgId": {
                                "extension": "QJ2"
                            },
                            "PrimaryRoleId": {
                                "id": ICB_ROLE_ID
                            }
                        },
                        "id": "RE4"
                    },
                    {
                        "Status": "Inactive",
                        "Target": {
                            "OrgId": {
                                "extension": "QJ2"
                            },
                            "PrimaryRoleId": {
                                "id": "NON_ICB_ROLE_ID"
                            }
                        },
                        "id": "RE4"
                    },
                ]
            }
        }
        result = _find_icb_ods_code(organisation)
        assert result is None

    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 200, "data": """{"Organisation": {"Name": "Practice 1"}}"""})())
    def test_fetch_organisation_returns_organisation_details(self, mock_PoolManager):
        an_organisation = {"Name": "Practice 1"}
        an_ods_code = "ODS_1"

        result = _fetch_organisation(an_ods_code)

        mock_PoolManager.assert_called_once_with('GET', ODS_PORTAL_URL + an_ods_code)
        assert result == an_organisation

    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 404, "data": """{}"""})())
    def test_fetch_organisation_returns_empty_organisation_when_no_matches_found(self, mock_PoolManager):
        an_ods_code = "ODS_1"

        result = _fetch_organisation(an_ods_code)

        mock_PoolManager.assert_called_once_with('GET', ODS_PORTAL_URL + an_ods_code)
        assert result == EMPTY_ORGANISATION

    @patch('urllib3.PoolManager.request',
           return_value=type('', (object,), {"status": 500, "data": """{}"""})())
    def test_fetch_organisation_throws_exception_when_500_status(self, mock_PoolManager):
        an_ods_code = "ODS_1"

        self.assertRaises(OdsPortalException, _fetch_organisation, an_ods_code)

        mock_PoolManager.assert_called_once_with('GET', ODS_PORTAL_URL + an_ods_code)
