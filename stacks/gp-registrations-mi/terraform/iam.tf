data "aws_caller_identity" "current" {}

resource "aws_iam_role" "gp_registrations_mi" {
  name               = "${var.environment}-gp-registrations-mi"
  description        = "Role for gp registrations mi ecs service"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
  managed_policy_arns = [
    aws_iam_policy.incoming_enriched_mi_events_sns_topic_publish.arn
  ]
}

data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = [
    "sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_api_gateway_rest_api_policy" "api_policy" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  policy      = data.aws_iam_policy_document.apigee_ip_policy.json
}

data "aws_iam_policy_document" "apigee_ip_policy" {
  statement {
    sid = "AllowApigeeIps"
    actions = [
      "execute-api:Invoke"
    ]
    resources = [
      "${aws_api_gateway_rest_api.rest_api.execution_arn}/${local.api_stage_name}/POST/*"
    ]
    condition {
      test     = "IpAddress"
      values   = split(",", data.aws_ssm_parameter.apigee_ips.value)
      variable = "aws:SourceIp"
    }
    principals {
      type        = "*"
      identifiers = ["*"]
    }
  }

  statement {
    sid = "AllowGETStatus"
    actions = [
      "execute-api:Invoke"
    ]
    resources = [
      "${aws_api_gateway_rest_api.rest_api.execution_arn}/${local.api_stage_name}/GET/_status"
    ]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
  }
}

data "aws_ssm_parameter" "apigee_ips" {
  name = var.apigee_ips_param_name
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "splunk_cloud_event_uploader_lambda_role" {
  name               = "${var.environment}-splunk_cloud-event-uploader-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.incoming_enriched_mi_events_for_splunk_cloud_uploader_lambda_sqs_read_access.arn,
    aws_iam_policy.splunk_cloud_uploader_lambda_ssm_access.arn,
    aws_iam_policy.splunk_cloud_event_uploader_lambda_cloudwatch_log_access.arn,
  ]
}

#SNS
data "aws_iam_policy_document" "incoming_enriched_mi_events_sns_topic" {
  statement {
    actions = [
      "sns:Publish",
      "sns:GetTopicAttributes"
    ]
    resources = [
      aws_sns_topic.enriched_mi_events.arn
    ]
  }
}

resource "aws_iam_policy" "incoming_enriched_mi_events_sns_topic_publish" {
  name   = "${aws_sns_topic.enriched_mi_events.name}-publish"
  policy = data.aws_iam_policy_document.incoming_enriched_mi_events_sns_topic.json
}

#SQS - Splunk Cloud lambda
resource "aws_sqs_queue_policy" "sqs_incoming_enriched_mi_events_for_splunk_cloud_uploader_send_message" {
  queue_url = aws_sqs_queue.incoming_enriched_mi_events_for_splunk_cloud_event_uploader.id
  policy    = data.aws_iam_policy_document.sqs_queue_incoming_enriched_mi_events_send_message.json
}

data "aws_iam_policy_document" "sqs_queue_incoming_enriched_mi_events_send_message" {
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
      aws_sqs_queue.incoming_enriched_mi_events_for_splunk_cloud_event_uploader.arn
    ]

    condition {
      test     = "ArnEquals"
      values   = [aws_sns_topic.enriched_mi_events.arn]
      variable = "aws:SourceArn"
    }
  }
}

resource "aws_iam_policy" "incoming_enriched_mi_events_for_splunk_cloud_uploader_lambda_sqs_read_access" {
  name   = "${var.environment}-incoming-enriched-mi-events-splunk-cloud-lambda-sqs-read"
  policy = data.aws_iam_policy_document.incoming_enriched_mi_events_for_splunk_cloud_event_uploader_lambda_sqs_read_access.json
}

data "aws_iam_policy_document" "incoming_enriched_mi_events_for_splunk_cloud_event_uploader_lambda_sqs_read_access" {
  statement {
    actions = [
      "sqs:GetQueue*",
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:ReceiveMessage"
    ]
    resources = [
      aws_sqs_queue.incoming_enriched_mi_events_for_splunk_cloud_event_uploader.arn,
    ]
  }
}

#SSM - Splunk Cloud lambda
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

#Cloudwatch - Splunk Cloud lambda
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

#Cloudwatch - SNS topic
resource "aws_iam_role" "sns_topic_enriched_mi_events_cloudwatch_log_access_role" {
  name               = "${var.environment}-sns-topic-enriched-mi-events-cloudwatch-log-access-role"
  assume_role_policy = data.aws_iam_policy_document.sns_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.sns_topic_enriched_mi_events_log_access.arn,
  ]
}

data "aws_iam_policy_document" "sns_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "sns_topic_enriched_mi_events_cloudwatch_log_access" {
  statement {
    sid = "CloudwatchLogs"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:PutMetricFilter",
      "logs:PutRetentionPolicy"
    ]
    resources = [
      "*",
    ]
  }
}

resource "aws_iam_policy" "sns_topic_enriched_mi_events_log_access" {
  name   = "${var.environment}-sns-topic-enriched-mi-events-cloudwatch-log-access"
  policy = data.aws_iam_policy_document.sns_topic_enriched_mi_events_cloudwatch_log_access.json
}

resource "aws_cloudwatch_log_group" "sns_topic_enriched_mi_events" {
  name = "/sns/${var.environment}-${var.enriched_mi_events_sns_topic_name}"
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-${var.enriched_mi_events_sns_topic_name}-cloudwatch"
    }
  )
  retention_in_days = 60
}