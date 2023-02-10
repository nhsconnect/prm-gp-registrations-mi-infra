#Lambda
resource "aws_iam_role" "error_alarm_alert_lambda_role" {
  name               = "${var.environment}-error-alarm-alert-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.error_alarm_alert_lambda_cloudwatch_log_access.arn,
    aws_iam_policy.error_alarm_alert_lambda_ssm_access.arn,
  ]
}

#SSM
resource "aws_iam_policy" "error_alarm_alert_lambda_ssm_access" {
  name   = "${var.environment}-error-alarm-alert-lambda-ssm-access"
  policy = data.aws_iam_policy_document.error_alarm_alert_lambda_ssm_access.json
}

data "aws_iam_policy_document" "error_alarm_alert_lambda_ssm_access" {
  statement {
    sid = "GetSSMParameter"

    actions = [
      "ssm:GetParameter"
    ]

    resources = [
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${var.log_alerts_general_webhook_url_param_name}",
    ]
  }
}

#Cloudwatch
resource "aws_iam_policy" "error_alarm_alert_lambda_cloudwatch_log_access" {
  name   = "${var.environment}-error-alarm-alert-lambda-log-access"
  policy = data.aws_iam_policy_document.error_alarm_alert_lambda_cloudwatch_log_access.json
}

data "aws_iam_policy_document" "error_alarm_alert_lambda_cloudwatch_log_access" {
  statement {
    sid = "CloudwatchLogs"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "${aws_cloudwatch_log_group.error_alarm_alert_lambda.arn}:*",
    ]
  }
}

resource "aws_cloudwatch_log_group" "error_alarm_alert_lambda" {
  name = "/aws/lambda/${var.environment}-${var.error_alarm_alert_lambda_name}"
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-${var.error_alarm_alert_lambda_name}-cloudwatch"
    }
  )
  retention_in_days = 60
}