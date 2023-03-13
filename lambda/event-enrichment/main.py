import json
import os
import boto3
import urllib3

ODS_PORTAL_URL = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/"
ICB_ROLE_ID = "RO98"
EMPTY_ORGANISATION = {"Name": None}

class OdsPortalException(Exception):
    pass


class UnableToGetIcbInformation(Exception):
    pass


class SsmSecretManager:
    def __init__(self, ssm):
        self._ssm = ssm

    def get_secret(self, name):
        response = self._ssm.get_parameter(Name=name, WithDecryption=True)
        return response["Parameter"]["Value"]


def lambda_handler(sqs_messages, context):
    try:
        print("[LAMBDA_STARTED][event-enrichment-lambda]")
        print("Enriching events - SQS Records: ", sqs_messages)
        enriched_events = _enrich_events(sqs_messages)
        print("[LAMBDA_SUCCESSFUL][event-enrichment-lambda]: Successfully enriched events:", enriched_events)
        _publish_enriched_events_to_sns_topic(enriched_events)
        return True
    except Exception as exception:
        print("[LAMBDA_FAILED][event-enrichment-lambda][ERROR]: Unable to enrich events. " + str(exception))
        raise exception
    finally:
        print("[LAMBDA_FINISHED][event-enrichment-lambda]")


def _enrich_events(sqs_messages):
    events_records = sqs_messages["Records"]
    events = [json.loads(event["body"]) for event in events_records]
    for event in events:
        if event["eventType"] == "DEGRADES":
            print("Skipping enrichment for degrades event with eventId: " + event["eventId"])
            continue

        requesting_practice_organisation = _fetch_organisation(event["requestingPracticeOdsCode"])
        event["requestingPracticeName"] = requesting_practice_organisation["Name"]
        event["requestingPracticeIcbOdsCode"] = _find_icb_ods_code(requesting_practice_organisation)
        event["requestingPracticeIcbName"] = _fetch_organisation(event["requestingPracticeIcbOdsCode"])["Name"]

        sending_practice_organisation = _fetch_organisation(event["sendingPracticeOdsCode"])
        event["sendingPracticeName"] = sending_practice_organisation["Name"]
        event["sendingPracticeIcbOdsCode"] = _find_icb_ods_code(sending_practice_organisation)
        event["sendingPracticeIcbName"] = _fetch_organisation(event["sendingPracticeIcbOdsCode"])["Name"]

    return events


def _find_icb_ods_code(practice_organisation):
    print("Finding ICB ODS code for practice organisation", practice_organisation)
    if not practice_organisation.get("Rels"):
        print("No ICB ODS code for practice organisation", practice_organisation)
        return None

    try:
        organisation_relationships = practice_organisation["Rels"]["Rel"]
        organisation_rel_containing_icb_code = next(
            organisation_details for organisation_details in organisation_relationships if
            _is_icb(organisation_details))

        if organisation_rel_containing_icb_code:
            print("Found organisation rel containing ICB ODS code: ", organisation_rel_containing_icb_code)
            return organisation_rel_containing_icb_code["Target"]["OrgId"]["extension"]  # ODS code
        else:
            print("No organisation rel containing ICB ODS code for organisation", practice_organisation)
            return None
    except Exception as e:
        print("Unable to find ICB information for practice " + str(practice_organisation), e)
        return None


def _is_icb(organisation_details):
    return organisation_details["Status"] == "Active" and organisation_details["Target"]["PrimaryRoleId"][
        "id"] == ICB_ROLE_ID


def _fetch_organisation(ods_code: str):
    if ods_code is None:
        return EMPTY_ORGANISATION

    print("Attempting to retrieve organisation with ODS code: " + ods_code)
    http = urllib3.PoolManager()
    response = http.request('GET', ODS_PORTAL_URL + ods_code)

    if response.status == 404:
        print("Unable to find organisation with ODS code: " + ods_code)
        return EMPTY_ORGANISATION

    if response.status != 200:
        raise OdsPortalException(
            "Unable to fetch organisation data for ODS code:" + ods_code + ". Response status code: " + str(
                response.status), response)

    print("Successfully retrieved organisation with ODS code: " + ods_code)
    response_content = json.loads(response.data)
    return response_content["Organisation"]


def _publish_enriched_events_to_sns_topic(enriched_events):
    print("Publishing enriched events to SNS", enriched_events)
    enriched_events_sns_topic_arn = os.environ["ENRICHED_EVENTS_SNS_TOPIC_ARN"]

    print("Sending:", json.dumps({'default': json.dumps(enriched_events)}))
    sns = boto3.client('sns')
    sns.publish(
        TargetArn=enriched_events_sns_topic_arn,
        Message=json.dumps({'default': json.dumps(enriched_events)}),
        MessageStructure='json'
    )


def _fetch_supplier_details(ods_code):
    http = urllib3.PoolManager()

    sds_fhir_api_url = os.environ["SDS_FHIR_API_URL"]

    http.request('GET', sds_fhir_api_url + ods_code)
