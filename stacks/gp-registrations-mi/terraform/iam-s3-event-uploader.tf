resource "aws_iam_role" "s3_event_uploader_role" {
  name = "${var.environment}-s3-event-uploader-role"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  managed_policy_arns = [
    aws_iam_policy.mi_events_output_s3_put_access.arn,
    aws_iam_policy.incoming_mi_events_for_s3_event_uploader_lambda_to_send_to_dlq_access.arn,
    aws_iam_policy.incoming_mi_events_for_s3_event_uploader_lambda_sqs_read_access.arn,
    aws_iam_policy.s3_event_uploader_lambda_cloudwatch_log_access.arn
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
      "arn:aws:s3:::${aws_s3_bucket.mi_events_output.bucket}/*"
    ]
  }
}

resource "aws_iam_policy" "incoming_mi_events_for_s3_event_uploader_lambda_sqs_read_access" {
  name   = "${var.environment}-incoming-mi-events-for-s3-event-uploader-lambda-sqs-read-access"
  policy = data.aws_iam_policy_document.incoming_mi_events_for_s3_event_uploader_lambda_sqs_read_access.json
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

#SQS - DLQ
resource "aws_iam_policy" "incoming_mi_events_for_s3_event_uploader_lambda_to_send_to_dlq_access" {
  name   = "${var.environment}-s3-event-uploader-lambda-send-to-dlq-access"
  policy = data.aws_iam_policy_document.incoming_mi_events_for_s3_event_uploader_lambda_to_send_to_dlq_access.json
}

data "aws_iam_policy_document" "incoming_mi_events_for_s3_event_uploader_lambda_to_send_to_dlq_access" {
  statement {

    effect = "Allow"

    actions = [
      "sqs:SendMessage"
    ]

    resources = [
      aws_sqs_queue.incoming_mi_events_for_s3_event_uploader_dlq.arn
    ]
  }
}

#Cloudwatch
resource "aws_iam_policy" "s3_event_uploader_lambda_cloudwatch_log_access" {
  name   = "${var.environment}-s3_event_uploader_lambda_log_access"
  policy = data.aws_iam_policy_document.s3_event_uploader_lambda_cloudwatch_log_access.json
}

data "aws_iam_policy_document" "s3_event_uploader_lambda_cloudwatch_log_access" {
  statement {
    sid = "CloudwatchLogs"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "${aws_cloudwatch_log_group.s3_event_uploader_lambda.arn}:*",
    ]
  }
}

# s3 event uploader sqs queue
resource "aws_sqs_queue_policy" "incoming_enriched_mi_events_for_s3_event_uploader" {
  queue_url = aws_sqs_queue.incoming_mi_events_for_s3_event_uploader.id
  policy    = data.aws_iam_policy_document.sqs_queue_incoming_enriched_mi_events_for_s3_event_uploader.json
}

data "aws_iam_policy_document" "sqs_queue_incoming_enriched_mi_events_for_s3_event_uploader" {
  statement {
    effect = "Allow"

    actions = [
      "sqs:SendMessage"
    ]

    principals {
      identifiers = ["sns.amazonaws.com"]
      type        = "Service"
    }

    resources = [
      aws_sqs_queue.incoming_mi_events_for_s3_event_uploader.arn,
    ]

    condition {
      test     = "ArnEquals"
      values   = [aws_sns_topic.enriched_events_topic.arn]
      variable = "aws:SourceArn"
    }
  }
}
