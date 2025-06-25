import json
import os
import unittest
from json import JSONDecodeError
from unittest.mock import patch, MagicMock

from event_enrichment_main import (
    _find_icb_ods_code,
    ICB_ROLE_ID,
    _fetch_organisation,
    ODS_PORTAL_URL,
    EMPTY_ORGANISATION,
    OdsPortalException,
    _enrich_events,
    _publish_enriched_events_to_sns_topic,
    lambda_handler,
    _fetch_supplier_details,
    _find_supplier_ods_codes_from_supplier_details,
    _has_supplier_ods_code,
    UnableToFetchSupplierDetailsFromSDSFHIRException,
    get_supplier_name_from_sds_api,
    UnableToMapSupplierOdsCodeToSupplierNameException,
)

A_VALID_TEST_ORGANISATION = {
    "Name": "Test Practice",
    "Rels": {
        "Rel": [
            {
                "Status": "Active",
                "Target": {
                    "OrgId": {"extension": "ODS_1"},
                    "PrimaryRoleId": {"id": ICB_ROLE_ID},
                },
            },
        ]
    },
}


def generate_successful_sds_fhir_api_response(supplier_ods_code: str) -> str:
    return json.dumps(
        {
            "entry": [
                {
                    "resource": {
                        "extension": [
                            {
                                "url": "https://fhir.nhs.uk/StructureDefinition/Extension-SDS-ManufacturingOrganisation",
                                "valueReference": {
                                    "identifier": {
                                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                                        "value": supplier_ods_code,
                                    }
                                },
                            }
                        ]
                    }
                }
            ]
        }
    )


def generate_successful_organisation(practice_ods_code: str):
    return {
        "Organisation": {
            "Name": "Test Practice",
            "Rels": {
                "Rel": [
                    {
                        "Status": "Active",
                        "Target": {
                            "OrgId": {"extension": practice_ods_code},
                            "PrimaryRoleId": {"id": "RO98"},
                        },
                    }
                ]
            },
        }
    }


def generate_side_effect(
        num_successful_organisation_to_generate: int,
        num_succesful_sds_fhir_api_responses_to_generate: int,
) -> list:
    side_effect_list = []

    for _ in range(num_successful_organisation_to_generate):
        side_effect_list.append(
            type(
                "",
                (object,),
                {
                    "status": 200,
                    "data": json.dumps(generate_successful_organisation("ODS_1")),
                },
            )()
        )

    for _ in range(num_succesful_sds_fhir_api_responses_to_generate):
        side_effect_list.append(
            type(
                "",
                (object,),
                {
                    "status": 200,
                    "data": generate_successful_sds_fhir_api_response("YGJ"),
                },
            )()
        )

    return side_effect_list


class TestEventEnrichmentMain(unittest.TestCase):
    @patch("urllib3.PoolManager.request", side_effect=generate_side_effect(4, 2))
    @patch("boto3.client")
    @patch.dict(os.environ, {"SDS_FHIR_API_KEY_PARAM_NAME": "test_fhir_api_key"})
    @patch.dict(os.environ, {"SDS_FHIR_API_URL_PARAM_NAME": "test_fhir_url"})
    @patch.dict(os.environ, {"SPLUNK_CLOUD_EVENT_UPLOADER_SQS_QUEUE_URL": "test_url"})
    @patch.dict(os.environ, {"ENRICHED_EVENTS_SNS_TOPIC_ARN": "test_arn"})
    def test_should_publish_enriched_event_with_lambda_handler(
            self, mock_boto, mock_request
    ):
        events = """{"eventId": "event_id_1", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1", "reportingSystemSupplier": "EMIS"}"""

        lambda_input = {"Records": [{"body": events}]}

        publish_spy = MagicMock()
        mock_boto("sns").publish = publish_spy

        result = lambda_handler(lambda_input, None)

        expected_events = json.dumps(
            [
                {
                    "eventId": "event_id_1",
                    "eventType": "REGISTRATIONS",
                    "requestingPracticeOdsCode": "ODS_1",
                    "sendingPracticeOdsCode": "ODS_1",
                    "reportingSystemSupplier": "EMIS",
                    "requestingPracticeName": "Test Practice",
                    "requestingPracticeIcbOdsCode": "ODS_1",
                    "requestingPracticeIcbName": "Test Practice",
                    "sendingPracticeName": "Test Practice",
                    "sendingPracticeIcbOdsCode": "ODS_1",
                    "sendingPracticeIcbName": "Test Practice",
                    "requestingSupplierName": "EMIS",
                    "sendingSupplierName": "EMIS",
                }
            ]
        )

        publish_spy.assert_called_once_with(
            TargetArn="test_arn",
            Message=json.dumps({"default": expected_events}),
            MessageStructure="json",
        )

        assert result is True

    @patch("urllib3.PoolManager.request", side_effect=generate_side_effect(4, 2))
    @patch("boto3.client")
    @patch.dict(os.environ, {"SDS_FHIR_API_KEY_PARAM_NAME": "test_fhir_api_key"})
    @patch.dict(os.environ, {"SDS_FHIR_API_URL_PARAM_NAME": "test_fhir_url"})
    def test_should_enrich_events_with_all_fields_from_organisation(
            self, mock_boto_client, mock_request
    ):
        events = """{"eventId": "event_id_1", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1", "reportingSystemSupplier":"EMIS"}"""

        lambda_input = {"Records": [{"body": events}]}

        result = _enrich_events(lambda_input)

        expected_events = [
            {
                "eventId": "event_id_1",
                "eventType": "REGISTRATIONS",
                "requestingPracticeOdsCode": "ODS_1",
                "sendingPracticeOdsCode": "ODS_1",
                "requestingPracticeName": "Test Practice",
                "requestingPracticeIcbOdsCode": "ODS_1",
                "requestingPracticeIcbName": "Test Practice",
                "sendingPracticeName": "Test Practice",
                "sendingPracticeIcbOdsCode": "ODS_1",
                "sendingPracticeIcbName": "Test Practice",
                "requestingSupplierName": "EMIS",
                "sendingSupplierName": "EMIS",
                "reportingSystemSupplier": "EMIS",
            }
        ]
        assert result == expected_events

    @patch("urllib3.PoolManager.request", side_effect=generate_side_effect(4, 2))
    @patch("boto3.client")
    @patch.dict(os.environ, {"SDS_FHIR_API_KEY_PARAM_NAME": "test_fhir_api_key"})
    @patch.dict(os.environ, {"SDS_FHIR_API_URL_PARAM_NAME": "test_fhir_url"})
    def test_should_correct_for_emis_sending_asid_code(
            self, mock_boto_client, mock_request
    ):
        """A temporary test to test that we can correct"""

        events = """{"eventId": "event_id_1", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ODS_1", "sendingPracticeOdsCode": "ODS_1", "reportingSystemSupplier":"200000000260"}"""

        lambda_input = {"Records": [{"body": events}]}

        result = _enrich_events(lambda_input)

        expected_events = [
            {
                "eventId": "event_id_1",
                "eventType": "REGISTRATIONS",
                "requestingPracticeOdsCode": "ODS_1",
                "sendingPracticeOdsCode": "ODS_1",
                "requestingPracticeName": "Test Practice",
                "requestingPracticeIcbOdsCode": "ODS_1",
                "requestingPracticeIcbName": "Test Practice",
                "sendingPracticeName": "Test Practice",
                "sendingPracticeIcbOdsCode": "ODS_1",
                "sendingPracticeIcbName": "Test Practice",
                "requestingSupplierName": "EMIS",
                "sendingSupplierName": "EMIS",
                "reportingSystemSupplier": "EMIS",
            }
        ]
        assert result == expected_events

    @patch("boto3.client")
    @patch(
        "urllib3.PoolManager.request",
        side_effect=[
            type("", (object,), {"status": 404, "data": A_VALID_TEST_ORGANISATION})(),
            type("", (object,), {"status": 404, "data": A_VALID_TEST_ORGANISATION})(),
            type(
                "",
                (object,),
                {
                    "status": 200,
                    "data": generate_successful_sds_fhir_api_response("YGJ"),
                },
            )(),
            type(
                "",
                (object,),
                {
                    "status": 200,
                    "data": generate_successful_sds_fhir_api_response("YGJ"),
                },
            )(),
        ],
    )
    @patch.dict(os.environ, {"SDS_FHIR_API_KEY_PARAM_NAME": "test_fhir_api_key"})
    @patch.dict(os.environ, {"SDS_FHIR_API_URL_PARAM_NAME": "test_fhir_url"})
    def test_should_enrich_events_with_empty_fields_if_unable_to_fetch_organisation(
            self, mock_boto_client, mock_requests
    ):
        events = """{"eventId": "event_id_1", "eventType": "REGISTRATIONS", "requestingPracticeOdsCode": "ods_1", "sendingPracticeOdsCode": "ods_2","reportingSystemSupplier":"EMIS"}"""

        lambda_input = {"Records": [{"body": events}]}

        result = _enrich_events(lambda_input)

        expected_events = [
            {
                "eventId": "event_id_1",
                "eventType": "REGISTRATIONS",
                "requestingPracticeOdsCode": "ods_1",
                "requestingPracticeIcbOdsCode": None,
                "requestingPracticeName": None,
                "requestingPracticeIcbName": None,
                "sendingPracticeOdsCode": "ods_2",
                "sendingPracticeName": None,
                "sendingPracticeIcbOdsCode": None,
                "sendingPracticeIcbName": None,
                "requestingSupplierName": "EMIS",
                "sendingSupplierName": "EMIS",
                "reportingSystemSupplier": "EMIS",
            }
        ]
        assert result == expected_events

    @patch.dict(os.environ, {"ENRICHED_EVENTS_SNS_TOPIC_ARN": "test_arn"})
    @patch("boto3.client")
    def test_uploads_events_to_sns(self, mock_boto):
        enriched_events = [{"someEvent": 1}]
        publish_spy = MagicMock()
        mock_boto("sns").publish = publish_spy

        _publish_enriched_events_to_sns_topic(enriched_events)
        event = '[{"someEvent": 1}]'

        publish_spy.assert_called_once_with(
            TargetArn="test_arn",
            Message=json.dumps({"default": event}),
            MessageStructure="json",
        )

    def test_find_icb_ods_code_returns_none_when_organisation_does_not_have_rels(self):
        organisation = {}
        result = _find_icb_ods_code(organisation)
        assert result is None

    def test_find_icb_ods_code_returns_ods_code_when_active_and_primary_role_id_is_an_icb_role(
            self,
    ):
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
                            "OrgId": {"extension": "QJ2"},
                            "PrimaryRoleId": {"id": "NON_ICB_ROLE_ID"},
                        },
                        "id": "RE4",
                    },
                ]
            },
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
                            "OrgId": {"extension": "QJ2"},
                            "PrimaryRoleId": {"id": ICB_ROLE_ID},
                        },
                        "id": "RE4",
                    },
                    {
                        "Status": "Inactive",
                        "Target": {
                            "OrgId": {"extension": "QJ2"},
                            "PrimaryRoleId": {"id": "NON_ICB_ROLE_ID"},
                        },
                        "id": "RE4",
                    },
                ]
            },
        }
        result = _find_icb_ods_code(organisation)
        assert result is None

    @patch(
        "urllib3.PoolManager.request",
        return_value=type(
            "",
            (object,),
            {"status": 200, "data": """{"Organisation": {"Name": "Practice 1"}}"""},
        )(),
    )
    def test_fetch_organisation_returns_organisation_details(self, mock_PoolManager):
        an_organisation = {"Name": "Practice 1"}
        an_ods_code = "ODS_1"

        result = _fetch_organisation(an_ods_code)

        mock_PoolManager.assert_called_once_with("GET", ODS_PORTAL_URL + an_ods_code)
        assert result == an_organisation

    @patch(
        "urllib3.PoolManager.request",
        return_value=type("", (object,), {"status": 404, "data": """{}"""})(),
    )
    def test_fetch_organisation_returns_empty_organisation_when_no_matches_found(
            self, mock_PoolManager
    ):
        an_ods_code = "ODS_1"

        result = _fetch_organisation(an_ods_code)

        mock_PoolManager.assert_called_once_with("GET", ODS_PORTAL_URL + an_ods_code)
        assert result == EMPTY_ORGANISATION

    @patch(
        "urllib3.PoolManager.request",
        return_value=type("", (object,), {"status": 500, "data": """{}"""})(),
    )
    def test_fetch_organisation_throws_exception_when_500_status(
            self, mock_PoolManager
    ):
        an_ods_code = "ODS_1"

        self.assertRaises(OdsPortalException, _fetch_organisation, an_ods_code)

        mock_PoolManager.assert_called_once_with("GET", ODS_PORTAL_URL + an_ods_code)

    def test_should_throw_exception_when_lambda_fails(self):
        lambda_input = {"Records": [{"body": ""}]}

        self.assertRaises(JSONDecodeError, lambda_handler, lambda_input, None)

    @patch.dict(os.environ, {"SDS_FHIR_API_URL_PARAM_NAME": "api-url-param-name"})
    @patch.dict(os.environ, {"SDS_FHIR_API_KEY_PARAM_NAME": "api-key-ssm-param-name"})
    @patch(
        "urllib3.PoolManager.request",
        return_value=type(
            "",
            (object,),
            {"status": 200, "data": generate_successful_sds_fhir_api_response("ODS_1")},
        )(),
    )
    @patch("boto3.client")
    def test_fetch_supplier_details(self, mock_boto3_client, mock_PoolManager):
        mock_boto3_client("ssm").get_parameter.side_effect = [
            {"Parameter": {"Value": "test-api-key"}},
            {"Parameter": {"Value": "some_url.net?"}},
        ]

        expected_sds_fhir_api_url = "some_url.net?"
        an_ods_code = "ODS_1"
        expected_headers = {"apiKey": "test-api-key"}

        response = _fetch_supplier_details(an_ods_code)

        mock_PoolManager.assert_called_once_with(
            method="GET",
            url=expected_sds_fhir_api_url + an_ods_code,
            headers=expected_headers,
        )
        expected_response = json.loads(
            generate_successful_sds_fhir_api_response("ODS_1")
        )

        assert response == expected_response

    @patch.dict(os.environ, {"SDS_FHIR_API_URL_PARAM_NAME": "api-url-param-name"})
    @patch.dict(os.environ, {"SDS_FHIR_API_KEY_PARAM_NAME": "api-key-ssm-param-name"})
    @patch(
        "urllib3.PoolManager.request",
        return_value=type("", (object,), {"status": 404, "data": """{}"""})(),
    )
    @patch("boto3.client")
    def test_fetch_supplier_details_throws_exception_when_non_200_status(
            self, mock_boto3_client, mock_PoolManager
    ):
        an_ods_code = "ODS_1"
        mock_boto3_client("ssm").get_parameter.side_effect = [
            {"Parameter": {"Value": "test-api-key"}},
            {"Parameter": {"Value": "some_url.net?"}},
        ]

        self.assertRaises(
            UnableToFetchSupplierDetailsFromSDSFHIRException,
            _fetch_supplier_details,
            an_ods_code,
        )

        expected_sds_fhir_api_url = "some_url.net?"
        expected_headers = {"apiKey": "test-api-key"}
        mock_PoolManager.assert_called_once_with(
            method="GET",
            url=expected_sds_fhir_api_url + an_ods_code,
            headers=expected_headers,
        )

    def test_find_supplier_ods_codes_from_supplier_details_given_3_entries(self):
        supplier_ods_code = "SUPPLIER_2"
        sds_fhir_api_ods_response = {
            "entry": [
                {"resource": {"extension": []}},
                {
                    "resource": {
                        "extension": [
                            {
                                "url": "https://fhir.nhs.uk/StructureDefinition/Extension-SDS-ManufacturingOrganisation",
                                "valueReference": {
                                    "identifier": {
                                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                                        "value": supplier_ods_code,
                                    }
                                },
                            },
                            {
                                "url": "https://fhir.nhs.uk/StructureDefinition/Extension-SDS-ManufacturingOrganisation",
                                "valueReference": {
                                    "identifier": {
                                        "system": "https://fhir.nhs.uk/Id/some_id",
                                        "value": "some_value",
                                    }
                                },
                            },
                            {
                                "url": "https://fhir.nhs.uk/StructureDefinition/Extension-SDS-NhsServiceInteractionId",
                                "valueReference": {
                                    "identifier": {
                                        "system": "https://fhir.nhs.uk/Id/nhsServiceInteractionId",
                                        "value": "urn:nhs:names:services:lrsquery:GET_RESOURCE_PERMISSIONS_INUK01",
                                    }
                                },
                            },
                        ]
                    }
                },
                {"resource": {"extension": []}},
            ]
        }

        result = _find_supplier_ods_codes_from_supplier_details(
            sds_fhir_api_ods_response
        )

        expected_result = supplier_ods_code

        assert expected_result in result

    def test_return_empty_list_when_supplier_details_has_no_ods_code(self):
        sds_fhir_api_ods_response = {
            "entry": [
                {"resource": {"extension": []}},
                {
                    "resource": {
                        "extension": [
                            {
                                "url": "https://fhir.nhs.uk/StructureDefinition/Extension-SDS-ManufacturingOrganisation",
                                "valueReference": {
                                    "identifier": {
                                        "system": "https://fhir.nhs.uk/Id/ods-organization-code"
                                    }
                                },
                            },
                            {
                                "url": "https://fhir.nhs.uk/StructureDefinition/Extension-SDS-ManufacturingOrganisation",
                                "valueReference": {
                                    "identifier": {
                                        "system": "https://fhir.nhs.uk/Id/some_id",
                                        "value": "some_value",
                                    }
                                },
                            },
                            {
                                "url": "https://fhir.nhs.uk/StructureDefinition/Extension-SDS-NhsServiceInteractionId",
                                "valueReference": {
                                    "identifier": {
                                        "system": "https://fhir.nhs.uk/Id/nhsServiceInteractionId",
                                        "value": "urn:nhs:names:services:lrsquery:GET_RESOURCE_PERMISSIONS_INUK01",
                                    }
                                },
                            },
                        ]
                    }
                },
                {"resource": {"extension": []}},
            ]
        }

        result = _find_supplier_ods_codes_from_supplier_details(
            sds_fhir_api_ods_response
        )

        assert not result

    def test_return_empty_list_when_supplier_details_is_empty(self):
        sds_fhir_api_ods_response = {}

        result = _find_supplier_ods_codes_from_supplier_details(
            sds_fhir_api_ods_response
        )

        assert not result

    def test_return_empty_list_when_supplier_details_has_entry_resources_but_no_extension(
            self,
    ):
        sds_fhir_api_ods_response = {"entry": [{"resource": {}}]}

        result = _find_supplier_ods_codes_from_supplier_details(
            sds_fhir_api_ods_response
        )

        assert not result

    def test_has_supplier_ods_code_no_SDS_ManufacturingOrganisation_fail(self):
        extension_response = {
            "url": "https://fhir.nhs.uk/StructureDefinition/Extension-",
            "valueReference": {
                "identifier": {"system": "https://fhir.nhs.uk/Id/ods-organization-code"}
            },
        }

        result = _has_supplier_ods_code(extension_response)

        assert result is False

    def test_has_supplier_ods_code_no_ods_organization_code_fail(self):
        extension_response = {
            "url": "https://fhir.nhs.uk/StructureDefinition/Extension-SDS-ManufacturingOrganisation",
            "valueReference": {"identifier": {"system": "https://fhir.nhs.uk/Id/"}},
        }

        result = _has_supplier_ods_code(extension_response)

        assert result is False

    @patch.dict(os.environ, {"SDS_FHIR_API_URL_PARAM_NAME": "api-url-param-name"})
    @patch.dict(os.environ, {"SDS_FHIR_API_KEY_PARAM_NAME": "api-key-ssm-param-name"})
    @patch(
        "urllib3.PoolManager.request",
        return_value=type(
            "",
            (object,),
            {"status": 200, "data": generate_successful_sds_fhir_api_response("YGJ")},
        ),
    )
    @patch("boto3.client")
    def test_returns_supplier_name_given_a_practice_ods_code(
            self, mock_boto3_client, _
    ):
        mock_boto3_client("ssm").get_parameter.side_effect = [
            {"Parameter": {"Value": "test-api-key"}},
            {"Parameter": {"Value": "some_url.net?"}},
        ]

        supplier_name = get_supplier_name_from_sds_api("test_supplier_ods_code")

        expected_supplier_name = "EMIS"
        assert supplier_name == expected_supplier_name

    @patch.dict(os.environ, {"SDS_FHIR_API_URL_PARAM_NAME": "api-url-param-name"})
    @patch.dict(os.environ, {"SDS_FHIR_API_KEY_PARAM_NAME": "api-key-ssm-param-name"})
    @patch(
        "urllib3.PoolManager.request",
        return_value=type("", (object,), {"status": 200, "data": """{}"""})(),
    )
    @patch("boto3.client")
    def test_supplier_name_returns_none_when_supplier_ods_code_is_not_found_from_sds_fhir_api_response(
            self, mock_boto3_client, _
    ):
        mock_boto3_client("ssm").get_parameter.side_effect = [
            {"Parameter": {"Value": "test-api-key"}},
            {"Parameter": {"Value": "some_url.net?"}},
        ]

        supplier_name = get_supplier_name_from_sds_api("PRACTICE_ODS_123")

        assert supplier_name is None

    @patch.dict(os.environ, {"SDS_FHIR_API_URL_PARAM_NAME": "api-url-param-name"})
    @patch.dict(os.environ, {"SDS_FHIR_API_KEY_PARAM_NAME": "api-key-ssm-param-name"})
    @patch(
        "urllib3.PoolManager.request",
        return_value=type("", (object,), {"status": 200, "data": """{}"""})(),
    )
    @patch("boto3.client")
    def test_supplier_name_returns_none_when_supplier_ods_code_is_none(
            self, mock_boto3_client, _
    ):
        mock_boto3_client("ssm").get_parameter.side_effect = [
            {"Parameter": {"Value": "test-api-key"}},
            {"Parameter": {"Value": "some_url.net?"}},
        ]

        supplier_name = get_supplier_name_from_sds_api(None)

        assert supplier_name is None

    @patch("boto3.client")
    @patch.dict(os.environ, {"DEGRADES_MESSAGE_QUEUE_NAME": "degrades_queue", "REGION": "us-east-2"})
    def test_degrades_message_sent_to_degrades_queue(
            self, mock_boto
    ):
        degrades_event = {"eventId": "01-DEGRADES-01",
                          "eventGeneratedDateTime": "2024-09-20T00:00:00",
                          "eventType": "DEGRADES",
                          "reportingSystemSupplier": "EMIS",
                          "payload": {"degrades": [{"type": "MEDICATION",
                                                    "reason": "CODE",
                                                    "coding": [{"code": "02543001",
                                                                "system": "UNKNOWN"
                                                                },
                                                               {
                                                                   "code": "02543001",
                                                                   "system": "UNKNOWN"
                                                               }]
                                                    }
                                                   ]
                                      }
                          }

        send_queue_spy = MagicMock()
        mock_boto("sqs").send_message = send_queue_spy

        get_url = MagicMock()
        mock_boto("sqs").get_queue_url = get_url
        get_url.return_value = {"QueueUrl": "queue_url"}

        lambda_input = {"Records": [{"body": json.dumps(degrades_event)}]}
        _enrich_events(lambda_input)

        send_queue_spy.assert_called_with(
            QueueUrl="queue_url",
            MessageBody=json.dumps(degrades_event)
        )
