import os

import boto3


def lambda_handler(sqs_messages, context):
    print("Uploading event to s3...")
    return _upload_events_to_s3(sqs_messages)


def _upload_events_to_s3(sqs_messages):
    events_list = _extract_events_from_sqs_messages(sqs_messages)
    s3_bucket = boto3.client('s3')
    for event in events_list:
        s3_bucket.put_object(Bucket=os.environ["MI_EVENTS_OUTPUT_S3_BUCKET_NAME"], Key="2000/01/02/09/event_id_1.json",
                             Body=event)
    return True


def _extract_events_from_sqs_messages(sqs_messages):
    event_records = sqs_messages["Records"]
    events_with_message_list = [(event_record["body"]) for event_record in
                                event_records]
    events = [(event_with_message["Message"]) for event_with_message in events_with_message_list][
        0]  # remove nested list created
    return events
