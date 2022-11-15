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
        print("Enriching events - SQS Records: ", sqs_messages)
        enriched_events = _enrich_events(sqs_messages)
        print("Successfully enriched events:", enriched_events)
        _send_enriched_events_to_sqs_for_uploading(enriched_events)
        return True
    except Exception as exception:
        print("Unable to enrich events. " + str(exception))
        return False


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
        event["requestingPracticeIcbName"] = _fetch_organisation_name(event["requestingPracticeIcbOdsCode"])

        if event["sendingPracticeOdsCode"]:
            sending_practice_organisation = _fetch_organisation(event["sendingPracticeOdsCode"])
            event["sendingPracticeName"] = sending_practice_organisation["Name"]
            event["sendingPracticeIcbOdsCode"] = _find_icb_ods_code(sending_practice_organisation)
            event["sendingPracticeIcbName"] = _fetch_organisation_name(event["sendingPracticeIcbOdsCode"])

    return events


def _find_icb_ods_code(practice_organisation):
    print("Finding icb_ods_code for practice organisation", practice_organisation)
    try:
        organisation_relationships = practice_organisation["Rels"]["Rel"]
        print("organisation_relationships", organisation_relationships)
        organisation_rel_containing_icb_code = next(
            organisation_details for organisation_details in organisation_relationships if _is_icb(organisation_details))

        if organisation_rel_containing_icb_code:
            print("Found organisation_rel_containing_icb_code", organisation_rel_containing_icb_code)
            return organisation_rel_containing_icb_code["Target"]["OrgId"]["extension"]
        else:
            print("No organisation_rel_containing_icb_code found for organisation", practice_organisation)
            return None
    except Exception as e:
        print("Unable to find icb information for practice " + str(practice_organisation), e)
        return None


def _is_icb(organisation_details):
    return organisation_details["Status"] == "Active" and organisation_details["Target"]["PrimaryRoleId"]["id"] == ICB_ROLE_ID


def _fetch_organisation_name(ods_code: str) -> str:
    return _fetch_organisation(ods_code)["Name"]


def _fetch_organisation(ods_code: str):
    if ods_code is None:
        return EMPTY_ORGANISATION

    print("Attempting to retrieve organisation with ods_code: " + ods_code)
    http = urllib3.PoolManager()
    response = http.request('GET', ODS_PORTAL_URL + ods_code)

    if response.status == 404:
        print("Unable to find organisation with ods code" + ods_code)
        return EMPTY_ORGANISATION

    if response.status != 200:
        raise OdsPortalException(
            "Unable to fetch organisation data for ods_code:" + ods_code + ". Response status code: " + str(
                response.status), response)

    print("Successfully retrieved organisation with ods_code: " + ods_code)
    response_content = json.loads(response.data.decode('utf-8'))
    return response_content["Organisation"]


def _send_enriched_events_to_sqs_for_uploading(enriched_events):
    print("Sending enriched events to SQS for uploading to splunk cloud", enriched_events)
    event_uploader_sqs_queue_url = os.environ["SPLUNK_CLOUD_EVENT_UPLOADER_SQS_QUEUE_URL"]

    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl=event_uploader_sqs_queue_url,
        MessageBody=json.dumps(enriched_events)
    )
