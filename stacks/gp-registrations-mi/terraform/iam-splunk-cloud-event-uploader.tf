#Lambda
resource "aws_iam_role" "splunk_cloud_event_uploader_lambda_role" {
  name               = "${var.environment}-splunk-cloud-event-uploader-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "mi_events_cloud_uploader_sqs_read_access" {
  role       = aws_iam_role.splunk_cloud_event_uploader_lambda_role.name
  policy_arn = aws_iam_policy.incoming_mi_events_for_splunk_cloud_uploader_lambda_sqs_read_access.arn
}

resource "aws_iam_role_policy_attachment" "mi_events_cloud_uploader_send_to_dlq_access" {
  role       = aws_iam_role.splunk_cloud_event_uploader_lambda_role.name
  policy_arn = aws_iam_policy.incoming_mi_events_for_splunk_cloud_uploader_lambda_to_send_to_dlq_access.arn
}

resource "aws_iam_role_policy_attachment" "lambda_ssm_access" {
  role       = aws_iam_role.splunk_cloud_event_uploader_lambda_role.name
  policy_arn = aws_iam_policy.splunk_cloud_uploader_lambda_ssm_access.arn
}

resource "aws_iam_role_policy_attachment" "splunk_cloudwatch_log_access" {
  role       = aws_iam_role.splunk_cloud_event_uploader_lambda_role.name
  policy_arn = aws_iam_policy.splunk_cloud_event_uploader_lambda_cloudwatch_log_access.arn
}

#SSM
resource "aws_iam_policy" "splunk_cloud_uploader_lambda_ssm_access" {
  name   = "${var.environment}-splunk-cloud-uploader-lambda-ssm-access"
  policy = data.aws_iam_policy_document.splunk_cloud_uploader_lambda_ssm_access.json
}

data "aws_iam_policy_document" "splunk_cloud_uploader_lambda_ssm_access" {
  statement {
    sid = "GetSSMParameter"

    actions = [
      "ssm:GetParameter"
    ]

    resources = [
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${var.splunk_cloud_url_param_name}",
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${var.splunk_cloud_api_token_param_name}",
    ]
  }
}

resource "aws_iam_policy" "incoming_mi_events_for_splunk_cloud_uploader_lambda_sqs_read_access" {
  name   = "${var.environment}-incoming-mi-events-splunk-cloud-lambda-sqs-read"
  policy = data.aws_iam_policy_document.incoming_mi_events_for_splunk_cloud_event_uploader_lambda_sqs_read_access.json
}

data "aws_iam_policy_document" "incoming_mi_events_for_splunk_cloud_event_uploader_lambda_sqs_read_access" {
  statement {
    actions = [
      "sqs:GetQueue*",
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:ReceiveMessage"
    ]
    resources = [
      aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader.arn,
    ]
  }
}

#SQS - DLQ
resource "aws_iam_policy" "incoming_mi_events_for_splunk_cloud_uploader_lambda_to_send_to_dlq_access" {
  name   = "${var.environment}-splunk-cloud-lambda-send-to-dlq-access"
  policy = data.aws_iam_policy_document.incoming_mi_events_for_splunk_cloud_uploader_lambda_to_send_to_dlq_access.json
}

data "aws_iam_policy_document" "incoming_mi_events_for_splunk_cloud_uploader_lambda_to_send_to_dlq_access" {
  statement {

    effect = "Allow"

    actions = [
      "sqs:SendMessage"
    ]

    resources = [
      aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader_dlq.arn
    ]
  }
}

#Cloudwatch
resource "aws_iam_policy" "splunk_cloud_event_uploader_lambda_cloudwatch_log_access" {
  name   = "${var.environment}-splunk-cloud-event-uploader-lambda-log-access"
  policy = data.aws_iam_policy_document.splunk_cloud_event_uploader_lambda_cloudwatch_log_access.json
}

data "aws_iam_policy_document" "splunk_cloud_event_uploader_lambda_cloudwatch_log_access" {
  statement {
    sid = "CloudwatchLogs"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "${aws_cloudwatch_log_group.splunk_cloud_event_uploader_lambda.arn}:*",
    ]
  }
}

# splunk event uploader sqs queue
resource "aws_sqs_queue_policy" "incoming_enriched_mi_events_for_splunk_cloud_event_uploader" {
  queue_url = aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader.id
  policy    = data.aws_iam_policy_document.sqs_queue_incoming_enriched_mi_events_for_splunk_cloud_event_uploader.json
}

data "aws_iam_policy_document" "sqs_queue_incoming_enriched_mi_events_for_splunk_cloud_event_uploader" {
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
      aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader.arn
    ]

    condition {
      test     = "ArnEquals"
      values   = [aws_sns_topic.enriched_events_topic.arn]
      variable = "aws:SourceArn"
    }
  }
}
