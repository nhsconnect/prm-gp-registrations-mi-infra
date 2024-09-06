import json
import os
from datetime import date, timedelta, datetime
from typing import Optional

import boto3
import urllib3

from utils.models.ods_models import PracticeOds, IcbOds

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
        requesting_practice_ods = event.get("requestingPracticeOdsCode")
        if requesting_practice_ods:
            event.update(
                _requesting_practice_info(
                    ods_code=requesting_practice_ods,
                    practice_name_key="requestingPracticeName",
                    icb_name_key="requestingPracticeIcbName",
                    icb_ods_code_key="requestingPracticeIcbOdsCode",
                    supplier_key="requestingSupplierName",
                )
            )
        else:
            print("Missing requestingPracticeOdsCode in event, skipping enrichment for requesting practice.")
        # set sending practice info
        sending_practice_ods = event.get("sendingPracticeOdsCode")
        if sending_practice_ods:
            event.update(
                _requesting_practice_info(
                    ods_code=sending_practice_ods,
                    practice_name_key="sendingPracticeName",
                    icb_name_key="sendingPracticeIcbName",
                    icb_ods_code_key="sendingPracticeIcbOdsCode",
                    supplier_key="sendingSupplierName",
                )
            )
        else:
            print("Missing sendingPracticeOdsCode in event, skipping enrichment for sending practice.")
        # temporary fix for EMIS wrong reportingSystemSupplier data
        reporting_system_supplier = event["reportingSystemSupplier"]
        if reporting_system_supplier.isnumeric():
            print(
                f"TEMP FIX. Reporting system supplier received: {reporting_system_supplier}. Changed to 'EMIS'."
            )
            event["reportingSystemSupplier"] = "EMIS"

    return events


def _requesting_practice_info(
    ods_code: str, practice_name_key: str, icb_name_key: str, icb_ods_code_key: str, supplier_key: str
) -> dict:
    enrichment_info = {}
    print("requesting data for: " + ods_code)
    gp_dynamo_item = arrange_gp_data_from_dynamo(ods_code) or get_gp_data_from_api(
        ods_code
    )
    if gp_dynamo_item:
        enrichment_info.update(
            {
                practice_name_key: gp_dynamo_item.practice_name,
                icb_ods_code_key: gp_dynamo_item.icb_ods_code,
            }
        )
        enrichment_info[supplier_key] = (
            get_supplier_data(ods_code, gp_dynamo_item) or "UNKNOWN"
        )
        enrichment_info[icb_name_key] = (
            get_icb_name(gp_dynamo_item.icb_ods_code) or "UNKNOWN"
        )
    else:
        enrichment_info[supplier_key] = "UNKNOWN"
    return enrichment_info


def arrange_gp_data_from_dynamo(ods_code: str):
    try:
        gp_dynamo_data = get_gp_data_from_dynamo_request(ods_code)
        print("Successfully query dynamo for GP data")
        return gp_dynamo_data
    except PracticeOds.DoesNotExist:
        print("Failed to find GP data in dynamo table")
        return None


def get_icb_name(ods_code: str):
    if ods_code is None:
        return None
    else:
        return get_icb_name_from_dynamo(ods_code) or get_icb_name_from_api(ods_code)


def get_icb_name_from_dynamo(ods_code: str):
    try:
        icb_dynamo_item = get_icb_data_from_dynamo_request(ods_code)
        print("Successfully query dynamo for ICB data")
        return icb_dynamo_item.icb_name
    except IcbOds.DoesNotExist:
        print("Failed to find ICB data in dynamo table")
        return None


def get_gp_data_from_api(ods_code: str):
    requesting_practice_organisation = _fetch_organisation(ods_code)

    practice_name = requesting_practice_organisation["Name"]
    if practice_name is None:
        return None
    icb_ods_code = _find_icb_ods_code(requesting_practice_organisation)
    gp_api_item = PracticeOds(ods_code, practice_name=practice_name, icb_ods_code=icb_ods_code)
    gp_api_item.save()
    return gp_api_item


def get_icb_name_from_api(ods_code: str):
    icb_name = _fetch_organisation(ods_code)["Name"]
    icb_api_item = IcbOds(ods_code, icb_name=icb_name)
    icb_api_item.save()
    return icb_name


def get_supplier_data(ods_code: str, gp_dynamo_item: PracticeOds):
    date_today = date.today()
    date_one_month_ago = date_today - timedelta(days=30)
    supplier_last_update_date = (
        gp_dynamo_item.supplier_last_updated.date()
        if gp_dynamo_item.supplier_last_updated
        else None
    )
    is_out_of_date = (
        supplier_last_update_date < date_one_month_ago
        if supplier_last_update_date
        else True
    )
    if not gp_dynamo_item.supplier_name or is_out_of_date:
        requesting_supplier_name = get_supplier_name_from_sds_api(ods_code)
        gp_dynamo_item.supplier_name = requesting_supplier_name
        gp_dynamo_item.update(
            actions=[
                PracticeOds.supplier_name.set(requesting_supplier_name),
                PracticeOds.supplier_last_updated.set(datetime.now()),
            ]
        )
    return gp_dynamo_item.supplier_name


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
    print("Requesting info from ODS API")
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
    if not practice_ods_code or practice_ods_code.isspace():
        return EMPTY_ORGANISATION

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


def get_supplier_name_from_sds_api(practice_ods_code: str) -> Optional[str]:
    """uses the SDS FHIR API to get the system supplier from an ODS code"""
    print("Requesting supplier info from SDS")
    if not practice_ods_code or practice_ods_code.isspace():
        return None

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
        print(
            f"Unable to map supplier ODS code(s) found from SDS FHI API: {str(supplier_ods_codes)}"
            + " to a known supplier name. Practice ODS code from event: {practice_ods_code}."
        )

    return supplier_name


def get_gp_data_from_dynamo_request(ods_code: str):
    return PracticeOds.get(ods_code)


def get_icb_data_from_dynamo_request(ods_code: str):
    return IcbOds.get(ods_code)
