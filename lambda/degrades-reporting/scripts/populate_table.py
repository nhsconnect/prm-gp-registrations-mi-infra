import json
import os
import boto3
from degrade_utils.s3_service import S3Service


def populate_degrades_table(date):
    bucket_name = os.getenv("REGISTRATIONS_MI_EVENT_BUCKET")
    sqs_client = boto3.client("sqs", region_name=os.getenv("REGION"))
    sqs_queue_url = sqs_client.get_queue_url(
        QueueName=os.getenv("DEGRADES_SQS_QUEUE_NAME")
    )

    s3_service = S3Service()
    print("Getting list of files from S3")
    file_keys = s3_service.list_files_from_S3(bucket_name=bucket_name, prefix=date)

    sum = 0

    for file_key in file_keys:
        print(f"Reading file:{file_key}")
        message = s3_service.get_file_from_S3(bucket_name=bucket_name, key=file_key)
        message_dict = json.loads(message)
        if message_dict["eventType"] == "DEGRADES":
            sum += 1
            print("Sending message to SQS, file key:", file_key)
            sqs_client.send_message(
                QueueUrl=sqs_queue_url["QueueUrl"], MessageBody=json.dumps(message_dict)
            )

    print(f"{date} has {sum} degrades messages")


if __name__ == "__main__":
    date = os.getenv("DATE")
    populate_degrades_table(date)
