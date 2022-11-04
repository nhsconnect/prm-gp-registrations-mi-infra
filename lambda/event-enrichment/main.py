import logging
from http.client import HTTPSConnection


class SsmSecretManager:
    def __init__(self, ssm):
        self._ssm = ssm

    def get_secret(self, name):
        response = self._ssm.get_parameter(Name=name, WithDecryption=True)
        return response["Parameter"]["Value"]


def lambda_handler(sqs_messages, context):
    try:
        print("Enriching event - messages: ", sqs_messages)
        _enrich_events(sqs_messages)
        print("Successfully enriched events", sqs_messages)
        return True
    except HTTPSConnection as exception:
        logging.error("Failed to enrich events. " + str(exception))
        return False


def _enrich_events(sqs_messages):
    print("Finished enriching")
