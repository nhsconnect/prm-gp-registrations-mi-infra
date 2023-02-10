import urllib3
import boto3
import json
import os

from botocore.exceptions import ClientError

http = urllib3.PoolManager()

class SsmSecretManager:
    def __init__(self, ssm):
        self._ssm = ssm

    def get_secret(self, name):
        response = self._ssm.get_parameter(Name=name, WithDecryption=True)
        return response["Parameter"]["Value"]


def lambda_handler(event, context):
    ssm = boto3.client("ssm")
    secret_manager = SsmSecretManager(ssm)

    # cloudwatch_dashboard_url = os.environ["CLOUDWATCH_DASHBOARD_URL"]
    #
    # text = (
    #     f"## **There was an error in the data pipeline:** <br>"
    #     f"See all the details in cloudwatch: {cloudwatch_dashboard_url}%<br>"
    # )

    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    error_alarm_text = f"##**{sns_message['AlarmName']}**\n{sns_message['AlarmDescription']}"

    error_alarm_msg = {
        "text": error_alarm_text,
        "textFormat": "markdown"
    }
    error_alarm_encoded_msg = json.dumps(error_alarm_msg).encode('utf-8')

    error_alarm_alert_webhook_url = secret_manager.get_secret(os.environ["LOG_ALERTS_GENERAL_WEBHOOK_URL_PARAM_NAME"])

    try:
        error_alarm_alert_resp = http.request('POST', url=error_alarm_alert_webhook_url, body=error_alarm_encoded_msg)

        print({
            "message": error_alarm_msg["text"],
            "status_code": error_alarm_alert_resp.status,
            "response": error_alarm_alert_resp.data,
            "alarm_name": sns_message['AlarmName'],
            "alarm_description": sns_message['AlarmDescription']
        })

    except ClientError as e:
        print(e.response['Error']['Message'])
    except Exception as e:
        print("An error has occurred: ", e)
    else:
        print("Successfully sent alerts")
