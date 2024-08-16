variable "error_alarm_alert_lambda_name" {
  default = "error-alarm-alert-lambda"
}

resource "aws_lambda_function" "error_alarm_alert_lambda" {
  filename         = var.error_alarm_alert_lambda_zip
  function_name    = "${var.environment}-${var.error_alarm_alert_lambda_name}"
  role             = aws_iam_role.error_alarm_alert_lambda_role.arn
  handler          = "error_alarm_alert_main.lambda_handler"
  source_code_hash = filebase64sha256(var.error_alarm_alert_lambda_zip)
  runtime          = "python3.12"
  timeout          = 15
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-error-alarm-alerts-lambda"
      ApplicationRole = "AwsLambdaFunction"
    }
  )

  environment {
    variables = {
      LOG_ALERTS_GENERAL_WEBHOOK_URL_PARAM_NAME = var.log_alerts_general_webhook_url_param_name,
      CLOUDWATCH_ALARM_URL                      = "${data.aws_region.current.name}.console.aws.amazon.com/cloudwatch/home#alarmsV2:?~(alarmStateFilter~'ALARM)",
      CLOUDWATCH_DASHBOARD_URL                  = "${data.aws_region.current.name}.console.aws.amazon.com/cloudwatch/home#dashboards:name=${aws_cloudwatch_dashboard.mi_api.dashboard_name}",
    }
  }
}
