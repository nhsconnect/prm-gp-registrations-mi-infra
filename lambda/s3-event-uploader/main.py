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
                             Body=event)
    return True


def _extract_events_from_sqs_messages(sqs_messages):
    print(sqs_messages)
    event_records = sqs_messages["Records"]
    print(event_records)
    events_with_message_list = [event_record["body"] for event_record in
                                event_records]
    print(events_with_message_list)
    events = [(json.loads(event_with_message)) for event_with_message in events_with_message_list]  # remove nested list created
    print(events)
    print("------"*10)
    events = [(json.loads(event_with_message["Message"])) for event_with_message in events_with_message_list]  # remove nested list created
    print(events)
    return events


def _generate_s3_key(event):
    event_object = json.loads(event)
    event_id = event_object["eventId"]
    event_date_time = event_object["registrationEventDateTime"]

    s3_path = datetime.datetime.strptime(event_date_time, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y/%m/%d/%H')
    return s3_path + "/" + event_id + ".json"
