#Lambda
resource "aws_iam_role" "event_enrichment_lambda_role" {
  name               = "${var.environment}event-enrichment-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.incoming_mi_events_for_event_enrichment_lambda_sqs_read_access.arn,
  ]
}

#SQS
resource "aws_iam_policy" "incoming_mi_events_for_event_enrichment_lambda_sqs_read_access" {
  name   = "${var.environment}-incoming-mi-events-enrichment-lambda-sqs-read"
  policy = data.aws_iam_policy_document.incoming_mi_events_for_event_enrichment_lambda_sqs_read_access.json
}

data "aws_iam_policy_document" "incoming_mi_events_for_event_enrichment_lambda_sqs_read_access" {
  statement {
    actions = [
      "sqs:GetQueue*",
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:ReceiveMessage"
    ]
    resources = [
      aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda.arn,
    ]
  }
}

#Cloudwatch
data "aws_iam_policy_document" "event_enrichment_lambda_cloudwatch_log_access" {
  statement {
    sid = "CloudwatchLogs"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "${aws_cloudwatch_log_group.event_enrichment_lambda.arn}:*",
    ]
  }
}

resource "aws_iam_policy" "event_enrichment_lambda_cloudwatch_log_access" {
  name   = "${var.environment}-event-enricher-lambda-log-access"
  policy = data.aws_iam_policy_document.event_enrichment_lambda_cloudwatch_log_access.json
}

resource "aws_cloudwatch_log_group" "event_enrichment_lambda" {
  name = "/aws/lambda/${var.environment}-${var.event_enrichment_lambda_name}"
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-${var.event_enrichment_lambda_name}"
    }
  )
  retention_in_days = 60
}