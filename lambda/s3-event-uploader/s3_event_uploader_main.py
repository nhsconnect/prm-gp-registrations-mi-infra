import datetime
import json
import os

import boto3


class UnableToUploadEventToS3(RuntimeError):
    pass


def lambda_handler(sqs_messages, context):
    try:
        print("[LAMBDA_STARTED][s3-event-uploader-lambda]")
        print("Uploading event to S3...")
        _upload_events_to_s3(sqs_messages)
        print("[LAMBDA_SUCCESSFUL][s3-event-uploader-lambda]: Successfully uploaded events to S3")
        return True
    except UnableToUploadEventToS3 as exception:
        print("[LAMBDA_FAILED][s3-event-uploader-lambda][ERROR] Failed to upload events to S3. " + str(exception))
        raise exception
    finally:
        print("[LAMBDA_FINISHED][s3-event-uploader-lambda]")


def _upload_events_to_s3(sqs_messages):
    print("Extracting events  - SQS Records: ", sqs_messages)
    events_list = _extract_events_from_sqs_messages(sqs_messages)
    print("Successfully extracted events:", events_list)
    s3_bucket = boto3.client('s3')
    print("Uploading events to S3...")
    try:
        for event in events_list:
            key = _generate_s3_key(event)
            event_id = event["eventId"]
            print(f"Attempting to upload event (eventId: {event_id}) to S3, with Key: {key}")
            s3_bucket.put_object(Bucket=os.environ["MI_EVENTS_OUTPUT_S3_BUCKET_NAME"], Key=key,
                                            Body=json.dumps(event))

            print("Successfully uploaded event with eventId: '" + event["eventId"] + "' to S3 ", event)
        return True
    except Exception as e:
        print("[ERROR] Unable to upload events to S3: ", e, str(events_list))
        raise UnableToUploadEventToS3()


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


def _generate_s3_key(event):
    event_id = event["eventId"]
    event_date_time = event["eventGeneratedDateTime"]
    s3_path = datetime.datetime.strptime(event_date_time, '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d')
    return s3_path + "/" + event_id + ".json"