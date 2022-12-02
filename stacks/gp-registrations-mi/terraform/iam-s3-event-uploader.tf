resource "aws_iam_role" "s3_event_uploader_role" {
  name = "${var.environment}-s3-event-uploader-role"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  managed_policy_arns = [
    aws_iam_policy.mi_events_output_s3_put_access.arn,
    aws_iam_policy.incoming_mi_events_for_s3_event_uploader_lambda_sqs_read_access.arn
  ]
}

resource "aws_iam_policy" "mi_events_output_s3_put_access" {
  name   = "${var.environment}-mi-events-output-s3-put-access"
  policy = data.aws_iam_policy_document.mi_events_output_s3_put_access.json

}

data "aws_iam_policy_document" "mi_events_output_s3_put_access" {
  statement {
    sid = "PutObjects"

    actions = [
      "s3:PutObject",
    ]

    resources = [
      aws_s3_bucket.mi_events_output.arn
    ]
  }
}

resource "aws_iam_policy" "incoming_mi_events_for_s3_event_uploader_lambda_sqs_read_access" {
  name   = "${var.environment}-incoming-mi-events-for-s3-event-uploader-lambda-sqs-read-access"
  policy = data.aws_iam_policy_document.incoming_mi_events_for_splunk_cloud_event_uploader_lambda_sqs_read_access.json
}

data "aws_iam_policy_document" "incoming_mi_events_for_s3_event_uploader_lambda_sqs_read_access" {
  statement {
    actions = [
      "sqs:GetQueue*",
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:ReceiveMessage"
    ]
    resources = [
      aws_sqs_queue.incoming_mi_events_for_s3_event_uploader.arn,
    ]
  }
}