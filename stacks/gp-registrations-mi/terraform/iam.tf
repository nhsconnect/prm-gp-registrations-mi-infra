resource "aws_iam_role" "gp_registrations_mi" {
  name               = "${var.environment}-gp-registrations-mi"
  description        = "Role for gp registrations mi ecs service"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
  managed_policy_arns = [
    aws_iam_policy.mi_output_bucket_write_access.arn,
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

resource "aws_iam_policy" "mi_output_bucket_write_access" {
  name   = "${aws_s3_bucket.mi_output.bucket}-write"
  policy = data.aws_iam_policy_document.mi_output_bucket_write_access.json
}

data "aws_iam_policy_document" "mi_output_bucket_write_access" {
  statement {
    sid = "WriteObjects"

    actions = [
      "s3:PutObject",
    ]

    resources = [
      "arn:aws:s3:::${aws_s3_bucket.mi_output.bucket}/*"
    ]
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

data "aws_iam_policy_document" "sqs_queue_incoming_enriched_mi_events" {
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
      aws_sqs_queue.incoming_enriched_mi_events_for_s3_event_uploader.arn
    ]

    condition {
      test     = "ArnEquals"
      values   = [aws_sns_topic.enriched_mi_events.arn]
      variable = "aws:SourceArn"
    }
  }
}

resource "aws_sqs_queue_policy" "incoming_enriched_mi_events_for_s3_event_uploader" {
  queue_url = aws_sqs_queue.incoming_enriched_mi_events_for_s3_event_uploader.id
  policy    = data.aws_iam_policy_document.sqs_queue_incoming_enriched_mi_events.json
}

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

resource "aws_cloudwatch_log_group" "s3_event_uploader_lambda" {
  name = "/aws/lambda/${aws_lambda_function.s3_event_uploader_lambda.function_name}"
  tags = merge(
    local.common_tags,
    {
      Name = aws_lambda_function.s3_event_uploader_lambda.function_name
    }
  )
  retention_in_days = 60
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

resource "aws_iam_policy" "s3_event_uploader_lambda_cloudwatch_log_access" {
  name   = "${var.environment}-s3-event-uploader-lambda-log-access"
  policy = data.aws_iam_policy_document.s3_event_uploader_lambda_cloudwatch_log_access.json
}

resource "aws_iam_policy" "incoming_enriched_mi_events_sns_topic_publish" {
  name   = "${aws_sns_topic.enriched_mi_events.name}-publish"
  policy = data.aws_iam_policy_document.incoming_enriched_mi_events_sns_topic.json
}

data "aws_iam_policy_document" "s3_event_uploader_lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "sqs_receive_incoming_enriched_mi_events_for_lambda" {
  name   = "${var.environment}-sqs-receive-incoming-enriched-mi-events-lambda"
  policy = data.aws_iam_policy_document.sqs_receive_incoming_enriched_mi_events_for_lambda.json
}

data "aws_iam_policy_document" "sqs_receive_incoming_enriched_mi_events_for_lambda" {
  statement {
    actions = [
      "sqs:GetQueue*",
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:ReceiveMessage"
    ]
    resources = [
      aws_sqs_queue.incoming_enriched_mi_events_for_s3_event_uploader.arn
    ]
  }
}
