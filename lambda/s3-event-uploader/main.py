import datetime
import json
import os

import boto3


def lambda_handler(sqs_messages, context):
    print("Uploading event to s3...")
    return _upload_events_to_s3(sqs_messages)


def _upload_events_to_s3(sqs_messages):
    events_list = _extract_events_from_sqs_messages(sqs_messages)
    s3_bucket = boto3.client('s3')
    for event in events_list:
        s3_bucket.put_object(Bucket=os.environ["MI_EVENTS_OUTPUT_S3_BUCKET_NAME"], Key=_generate_s3_key(event),
                             Body=json.dumps(event))
    return True


def _extract_events_from_sqs_messages(sqs_messages):
    event_records = sqs_messages["Records"]
    event_records_list = [json.loads(event_record["body"]) for event_record in
                          event_records]
    events = [(json.loads(event_with_message["Message"])) for event_with_message in event_records_list][0]  # remove nested list created
    return events


def _generate_s3_key(event):
    event_id = event["eventId"]
    event_date_time = event["registrationEventDateTime"]
    s3_path = datetime.datetime.strptime(event_date_time, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y/%m/%d/%H')
    return s3_path + "/" + event_id + ".json"