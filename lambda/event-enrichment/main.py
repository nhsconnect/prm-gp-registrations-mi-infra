import os
import boto3


class SsmSecretManager:
    def __init__(self, ssm):
        self._ssm = ssm

    def get_secret(self, name):
        response = self._ssm.get_parameter(Name=name, WithDecryption=True)
        return response["Parameter"]["Value"]


def lambda_handler(sqs_messages, context):
    try:
        print("Enriching event - messages: ", sqs_messages)
        enriched_events = _enrich_events(sqs_messages)
        print("Successfully enriched events. Preparing to upload", enriched_events)
        _send_enriched_events_to_sqs_for_uploading(enriched_events)
        print("Successfully enriched events and sent to SQS event uploader", enriched_events)
        return True
    except Exception as exception:
        print("Failed to enrich events. " + str(exception))
        return False


def _enrich_events(sqs_messages):
    print("Finished enriching")
    return "test"


def _send_enriched_events_to_sqs_for_uploading(enriched_events):
    ssm = boto3.client("ssm")
    secret_manager = SsmSecretManager(ssm)
    event_uploader_sqs_queue_url = secret_manager.get_secret(os.environ["SPLUNK_CLOUD_EVENT_UPLOADER_SQS_QUEUE_URL"])

    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl=event_uploader_sqs_queue_url,
        MessageBody=enriched_events
    )
