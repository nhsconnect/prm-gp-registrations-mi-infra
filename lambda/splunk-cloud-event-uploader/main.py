import os
import json
import boto3
import urllib3


class UnableToSendEventToSplunkCloud(RuntimeError):
    pass


class SsmSecretManager:
    def __init__(self, ssm):
        self._ssm = ssm

    def get_secret(self, name):
        response = self._ssm.get_parameter(Name=name, WithDecryption=True)
        return response["Parameter"]["Value"]


def lambda_handler(sqs_messages, context):
    try:
        print("Sending events to splunk cloud: ", sqs_messages)
        events = _extract_events_from_sqs_messages(sqs_messages)
        _send_events_to_splunk_cloud(events)
        print("Successfully sent events to Splunk Cloud", sqs_messages)
        return True
    except UnableToSendEventToSplunkCloud as exception:
        print("[ERROR] Failed to send events to Splunk Cloud. " + str(exception))
        raise exception


def _extract_events_from_sqs_messages(sqs_messages):
    event_records = sqs_messages["Records"]
    event_records_list = [json.loads(event_record["body"]) for event_record in
                          event_records]
    events_nested_list = [(json.loads(event_with_message["Message"])) for event_with_message in event_records_list]
    # flatten list:
    events = []
    for list_of_events in events_nested_list:
        for event in list_of_events:
            events.append(event)
    return events


def _send_events_to_splunk_cloud(events):
    ssm = boto3.client("ssm")
    secret_manager = SsmSecretManager(ssm)
    splunk_cloud_api_token = secret_manager.get_secret(os.environ["SPLUNK_CLOUD_API_TOKEN"])
    splunk_cloud_url = secret_manager.get_secret(os.environ["SPLUNK_CLOUD_URL"])

    http = urllib3.PoolManager()

    try:
        for event in events:
            print("Attempting to send event to Splunk Cloud with eventId: '" + event["eventId"] + "'", event)

            request_body = json.dumps({
                "source": "itoc:gp2gp",
                "event": event
            })

            headers = {"Authorization": splunk_cloud_api_token}

            response = http.request(method='POST', url=splunk_cloud_url, headers=headers, body=request_body)

            if response.status != 200:
                raise UnableToSendEventToSplunkCloud(
                    f"Splunk request returned a {response.status} code with body {response.data}. With eventId: '" +
                    event["eventId"] + "'", event)

            print("Successfully sent event to Splunk Cloud with eventId: '" + event["eventId"] + "'", event)
        return True
    except Exception as e:
        print("[ERROR] Unable to send events to Splunk Cloud: ", e, str(events))
        raise UnableToSendEventToSplunkCloud()
