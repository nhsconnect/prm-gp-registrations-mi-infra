import json
import os
from typing import Optional

import boto3
import urllib3

ODS_PORTAL_URL = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/"
ICB_ROLE_ID = "RO98"
EMPTY_ORGANISATION = {"Name": None}


class OdsPortalException(Exception):
    pass


class UnableToGetIcbInformation(Exception):
    pass


class UnableToFetchSupplierDetailsFromSDSFHIRException(Exception):
    pass


class UnableToMapSupplierOdsCodeToSupplierNameException(Exception):
    pass


class SsmSecretManager:
    def __init__(self, ssm):
        self._ssm = ssm

    def get_secret(self, name):
        response = self._ssm.get_parameter(Name=name, WithDecryption=True)
        return response["Parameter"]["Value"]


def lambda_handler(sqs_messages: dict, context):
    try:
        print("[LAMBDA_STARTED][event-enrichment-lambda]")
        print("Enriching events - SQS Records: ", sqs_messages)
        enriched_events = _enrich_events(sqs_messages)
        print(
            "[LAMBDA_SUCCESSFUL][event-enrichment-lambda]: Successfully enriched events:",
            enriched_events,
        )
        _publish_enriched_events_to_sns_topic(enriched_events)
        return True
    except Exception as exception:
        print(
            "[LAMBDA_FAILED][event-enrichment-lambda][ERROR]: Unable to enrich events. "
            + str(exception)
        )
        raise exception
    finally:
        print("[LAMBDA_FINISHED][event-enrichment-lambda]")


def _enrich_events(sqs_messages: dict) -> list:
    events_records = sqs_messages["Records"]
    events = [json.loads(event["body"]) for event in events_records]
    for event in events:
        if event["eventType"] == "DEGRADES":
            print(
                f"Skipping enrichment for degrades event with eventId: {event['eventId']}."
            )
            continue
        
        # set requesting practice info
        requesting_practice_organisation = _fetch_organisation(
            event["requestingPracticeOdsCode"]
        )
        event["requestingPracticeName"] = requesting_practice_organisation["Name"]
        event["requestingPracticeIcbOdsCode"] = _find_icb_ods_code(
            requesting_practice_organisation
        )
        event["requestingPracticeIcbName"] = _fetch_organisation(
            event["requestingPracticeIcbOdsCode"]
        )["Name"]

        # set sending practice info
        sending_practice_organisation = _fetch_organisation(
            event["sendingPracticeOdsCode"]
        )
        event["sendingPracticeName"] = sending_practice_organisation["Name"]
        event["sendingPracticeIcbOdsCode"] = _find_icb_ods_code(
            sending_practice_organisation
        )
        event["sendingPracticeIcbName"] = _fetch_organisation(
            event["sendingPracticeIcbOdsCode"]
        )["Name"]

        # set requesting supplier info
        requesting_supplier_name = get_supplier_name(event["requestingPracticeOdsCode"])
        event["requestingSupplierName"] = (
            requesting_supplier_name
            if requesting_supplier_name is not None
            else "UNKNOWN"
        )

        # set sending supplier info
        sending_supplier_name = get_supplier_name(event["sendingPracticeOdsCode"])
        event["sendingSupplierName"] = (
            sending_supplier_name 
            if sending_supplier_name is not None 
            else "UNKNOWN"
        )

    return events


def _find_icb_ods_code(practice_organisation: dict) -> Optional[str]:
    print("Finding ICB ODS code for practice organisation", practice_organisation)
    if not practice_organisation.get("Rels"):
        print("No ICB ODS code for practice organisation", practice_organisation)
        return None

    try:
        organisation_relationships = practice_organisation["Rels"]["Rel"]
        organisation_rel_containing_icb_code = next(
            organisation_details
            for organisation_details in organisation_relationships
            if _is_icb(organisation_details)
        )

        if organisation_rel_containing_icb_code:
            print(
                "Found organisation rel containing ICB ODS code: ",
                organisation_rel_containing_icb_code,
            )
            return organisation_rel_containing_icb_code["Target"]["OrgId"][
                "extension"
            ]  # ODS code
        else:
            print(
                "No organisation rel containing ICB ODS code for organisation",
                practice_organisation,
            )
            return None
    except Exception as e:
        print(
            "Unable to find ICB information for practice " + str(practice_organisation),
            e,
        )
        return None


def _is_icb(organisation_details: dict) -> bool:
    return (
        organisation_details["Status"] == "Active"
        and organisation_details["Target"]["PrimaryRoleId"]["id"] == ICB_ROLE_ID
    )


def _fetch_organisation(ods_code: Optional[str]) -> dict:
    if ods_code is None:
        return EMPTY_ORGANISATION

    print("Attempting to retrieve organisation with ODS code: " + ods_code)
    http = urllib3.PoolManager()
    response = http.request("GET", ODS_PORTAL_URL + ods_code)

    if response.status == 404:
        print("Unable to find organisation with ODS code: " + ods_code)
        return EMPTY_ORGANISATION

    if response.status != 200:
        raise OdsPortalException(
            "Unable to fetch organisation data for ODS code:"
            + ods_code
            + ". Response status code: "
            + str(response.status),
            response,
        )

    print("Successfully retrieved organisation with ODS code: " + ods_code)
    response_content = json.loads(response.data)
    return response_content["Organisation"]


def _publish_enriched_events_to_sns_topic(enriched_events: list):
    print("Publishing enriched events to SNS", enriched_events)
    enriched_events_sns_topic_arn = os.environ["ENRICHED_EVENTS_SNS_TOPIC_ARN"]

    print("Sending:", json.dumps({"default": json.dumps(enriched_events)}))
    sns = boto3.client("sns")
    sns.publish(
        TargetArn=enriched_events_sns_topic_arn,
        Message=json.dumps({"default": json.dumps(enriched_events)}),
        MessageStructure="json",
    )


def _fetch_supplier_details(practice_ods_code: str) -> dict:
    http = urllib3.PoolManager()
    ssm = boto3.client("ssm")
    secret_manager = SsmSecretManager(ssm)

    sds_fhir_api_key = secret_manager.get_secret(
        os.environ["SDS_FHIR_API_KEY_PARAM_NAME"]
    )
    sds_fhir_api_url = secret_manager.get_secret(
        os.environ["SDS_FHIR_API_URL_PARAM_NAME"]
    )

    headers = {"apiKey": sds_fhir_api_key}
    response = http.request(
        method="GET", url=sds_fhir_api_url + practice_ods_code, headers=headers
    )

    if response.status != 200:
        raise UnableToFetchSupplierDetailsFromSDSFHIRException(
            f"Unable to fetch supplier details from SDS FHIR API with practice ods code: {practice_ods_code}.\n"
            + f"Response status code: {str(response.status)} ",
            response,
        )

    response_content = json.loads(response.data)

    return response_content


def _has_supplier_ods_code(extension: dict) -> bool:
    return (
        "SDS-ManufacturingOrganisation" in extension["url"]
        and "ods-organization-code"
        in extension["valueReference"]["identifier"]["system"]
    )


def _find_supplier_ods_codes_from_supplier_details(supplier_details: dict) -> list:
    supplier_ods_codes = []
    extension = None  # set extension to none for error logging purposes

    try:
        for entry in supplier_details["entry"]:
            for extension in entry["resource"]["extension"]:
                if _has_supplier_ods_code(extension):
                    supplier_ods_codes.append(
                        extension["valueReference"]["identifier"]["value"]
                    )
    except Exception as exception:
        print(
            f"Unable to find supplier ODS code from SDS FHIR API response. Exception type: {str(type(exception))}\n"
            + " Exception: {str(exception)}"
        )
        return []

    return supplier_ods_codes


def get_supplier_name(practice_ods_code: str) -> Optional[str]:
    """uses the SDS FHIR API to get the system supplier from an ODS code"""
    supplier_details = _fetch_supplier_details(practice_ods_code)
    supplier_ods_codes = _find_supplier_ods_codes_from_supplier_details(
        supplier_details
    )

    supplier_name_mapping = {
        "YGJ": "EMIS",
        "YGA": "SystmOne",
        "YGC": "Vision",
    }

    supplier_name = None
    
    for supplier_ods_code in supplier_ods_codes:
        try:
            supplier_name = supplier_name_mapping[supplier_ods_code]
            if supplier_name is not None:
                break
        except KeyError:
            continue
    
    if supplier_name is None:
        raise UnableToMapSupplierOdsCodeToSupplierNameException()
        # print(
        #     f"Unable to map supplier ODS code(s) found from SDS FHI API: {str(supplier_ods_codes)}"
        #     + " to a known supplier name. Practice ODS code from event: {practice_ods_code}."
        # )    

    return supplier_name
    
    