#Lambda
resource "aws_iam_role" "splunk_cloud_event_uploader_lambda_role" {
  name               = "${var.environment}-splunk-cloud-event-uploader-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.incoming_mi_events_for_splunk_cloud_uploader_lambda_sqs_read_access.arn,
    aws_iam_policy.splunk_cloud_uploader_lambda_ssm_access.arn,
    aws_iam_policy.splunk_cloud_event_uploader_lambda_cloudwatch_log_access.arn,
  ]
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

#Cloudwatch
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

resource "aws_iam_policy" "splunk_cloud_event_uploader_lambda_cloudwatch_log_access" {
  name   = "${var.environment}-splunk-cloud-event-uploader-lambda-log-access"
  policy = data.aws_iam_policy_document.splunk_cloud_event_uploader_lambda_cloudwatch_log_access.json
}

resource "aws_cloudwatch_log_group" "splunk_cloud_event_uploader_lambda" {
  name = "/aws/lambda/${var.environment}-${var.splunk_cloud_event_uploader_lambda_name}"
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-${var.splunk_cloud_event_uploader_lambda_name}"
    }
  )
  retention_in_days = 60
}
