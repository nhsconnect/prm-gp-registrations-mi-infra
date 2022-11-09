import json


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
        return enriched_events
    except Exception as exception:
        print("Failed to enrich events. " + str(exception))
        return False


def _enrich_events(sqs_messages):
    events = sqs_messages["Records"]
    return [json.loads(event["body"]) for event in events]
