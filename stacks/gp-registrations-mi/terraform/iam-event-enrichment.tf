#Lambda
resource "aws_iam_role" "event_enrichment_lambda_role" {
  name               = "${var.environment}-event-enrichment-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.incoming_mi_events_for_event_enrichment_lambda_sqs_read_access.arn,
    aws_iam_policy.incoming_event_enrichment_lambda_to_send_to_dlq_access.arn,
    aws_iam_policy.event_enrichment_lambda_cloudwatch_log_access.arn,
    aws_iam_policy.enriched_mi_events_sns_publish_access.arn,
    aws_iam_policy.event_enrichment_lambda_ssm_access.arn,
    aws_iam_policy.dynamodb_policy_ods_enrichment_lambda.arn,
    aws_iam_policy.dynamodb_policy_icb_ods_enrichment_lambda.arn
  ]
}

resource "aws_iam_role" "bulk_ods_lambda" {
  name               = "${var.environment}-bulk-ods-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.dynamodb_policy_bulk_icb_ods_data_lambda.arn,
    aws_iam_policy.dynamodb_policy_bulk_ods_data_lambda.arn,
    aws_iam_policy.bulk_ods_update_lambda_cloudwatch_log_access.arn,
    aws_iam_policy.ods_csv_files_data_policy.arn,
    aws_iam_policy.bulk_ods_lambda_ssm_access.arn
  ]
}

#SSM
resource "aws_iam_policy" "event_enrichment_lambda_ssm_access" {
  name   = "${var.environment}-event-enrichment-lambda-ssm-access"
  policy = data.aws_iam_policy_document.event_enrichment_lambda_ssm_access.json
}

data "aws_iam_policy_document" "event_enrichment_lambda_ssm_access" {
  statement {
    sid = "GetSSMParameter"

    actions = [
      "ssm:GetParameter"
    ]
    resources = [
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${var.sds_fhir_api_key_param_name}",
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${var.sds_fhir_api_url_param_name}",
    ]
  }
}

resource "aws_iam_policy" "bulk_ods_lambda_ssm_access" {
  name   = "${var.environment}-bulk-ods-lambda-ssm-access"
  policy = data.aws_iam_policy_document.bulk_ods_lambda_ssm_access.json
}

data "aws_iam_policy_document" "bulk_ods_lambda_ssm_access" {
  statement {
    sid = "GetSSMParameter"

    actions = [
      "ssm:GetParameter"
    ]
    resources = [
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${data.aws_ssm_parameter.trud_api_key.name}"
    ]
  }
}

#SQS - inbound
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

#SQS - DLQ
resource "aws_iam_policy" "incoming_event_enrichment_lambda_to_send_to_dlq_access" {
  name   = "${var.environment}-event-enrichment-lambda-send-to-dlq-access"
  policy = data.aws_iam_policy_document.incoming_event_enrichment_lambda_to_send_to_dlq_access.json
}

data "aws_iam_policy_document" "incoming_event_enrichment_lambda_to_send_to_dlq_access" {
  statement {

    effect = "Allow"

    actions = [
      "sqs:SendMessage"
    ]
    resources = [
      aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda_dlq.arn
    ]
  }
}

#Cloudwatch
resource "aws_iam_policy" "event_enrichment_lambda_cloudwatch_log_access" {
  name   = "${var.environment}-event-enricher-lambda-log-access"
  policy = data.aws_iam_policy_document.event_enrichment_lambda_cloudwatch_log_access.json
}

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


resource "aws_iam_policy" "bulk_ods_update_lambda_cloudwatch_log_access" {
  name   = "${var.environment}-bulk-ods-update-lambda-log-access"
  policy = data.aws_iam_policy_document.bulk_ods_update_lambda_cloudwatch_log_access.json
}

data "aws_iam_policy_document" "bulk_ods_update_lambda_cloudwatch_log_access" {
  statement {
    sid = "CloudwatchLogs"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "${aws_cloudwatch_log_group.bulk_ods_update_lambda.arn}:*",
    ]
  }
}