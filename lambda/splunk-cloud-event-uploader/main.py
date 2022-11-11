import logging
import os
import json
from json import JSONDecodeError

import boto3
from urllib.parse import urlparse
from http.client import HTTPSConnection


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
        _send_events_to_splunk_cloud(sqs_messages)
        print("Successfully sent events to Splunk Cloud", sqs_messages)
        return True
    except UnableToSendEventToSplunkCloud as exception:
        logging.error("Failed to send events to Splunk Cloud. " + str(exception))
        return False


def _send_events_to_splunk_cloud(sqs_messages):
    ssm = boto3.client("ssm")
    secret_manager = SsmSecretManager(ssm)
    splunk_cloud_api_token = secret_manager.get_secret(os.environ["SPLUNK_CLOUD_API_TOKEN"])
    splunk_cloud_url = secret_manager.get_secret(os.environ["SPLUNK_CLOUD_URL"])
    splunk_cloud_base_url = urlparse(splunk_cloud_url).netloc
    splunk_cloud_endpoint_path = urlparse(splunk_cloud_url).path

    connection = HTTPSConnection(splunk_cloud_base_url)
    connection.connect()

    event_records = sqs_messages["Records"]
    events = [json.loads(event_record["body"]) for event_record in event_records][0]
    try:
        for event in events:
            print("Attempting to send event to Splunk Cloud with eventId: '" + event["eventId"] + "'", event)

            request_body = json.dumps({
                "source": "itoc:gp2gp",
                "event": event
            })

            headers = {"Authorization": splunk_cloud_api_token}
            connection.request(
                'POST', splunk_cloud_endpoint_path, request_body, headers)

            response = connection.getresponse()

            if response.status != 200:
                raise UnableToSendEventToSplunkCloud(
                    f"Splunk request returned a {response.status} code with body {response.read()}. With eventId: '" +
                    event["eventId"] + "'", event)

            print("Successfully sent event to Splunk Cloud with eventId: '" + event["eventId"] + "'", event)

            return response.read()
    except JSONDecodeError as e:
        print("Unable to parse JSON:" + str(event_records), e)
        raise UnableToSendEventToSplunkCloud()
