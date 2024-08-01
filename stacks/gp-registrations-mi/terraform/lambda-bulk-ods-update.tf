resource "aws_lambda_function" "ods_bulk_update" {
  filename         = "${path.cwd}/${var.ods_bulk_update_lambda_name}"
  function_name    = "${var.environment}-${var.ods_bulk_update_lambda_name}"
  role             = aws_iam_role.bulk_ods_lambda.arn
  handler          = "ods_bulk_update.lambda_handler"
  source_code_hash = filebase64sha256(var.bulk_ods_update_lambda_zip)
  runtime          = "python3.12"
  timeout          = 300
  environment {
    variables = {
      TRUD_API_KEY_PARAM_NAME      = data.aws_ssm_parameter.trud_api_key.value,
      TRUD_FHIR_API_URL_PARAM_NAME = data.aws_ssm_parameter.trud_api_endpoint.value,
    }
  }
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-mi-ods_bulk"
      ApplicationRole = "AwsLambdaFunction"
    }
  )
}

resource "aws_cloudwatch_log_group" "bulk_ods_update_lambda" {
  name = "/aws/lambda/${var.environment}-${var.ods_bulk_update_lambda_name}"
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-${var.ods_bulk_update_lambda_name}"
      ApplicationRole = "AwsCloudwatchLogGroup"
    }
  )
  retention_in_days = 60
}

data "aws_ssm_parameter" "trud_api_key" {
  name = "/registrations/dev/user-input/trud-api-key"
}

data "aws_ssm_parameter" "trud_api_endpoint" {
  name = "/registrations/dev/user-input/trud-api-url"
}

resource "aws_cloudwatch_event_rule" "ods_bulk_update_schedule" {
  name                = "${var.environment}_ods_bulk_update_schedule"
  description         = "Schedule for ODS Update Lambda"
  schedule_expression = "cron(0 1 ? * 1 *)"
}

resource "aws_cloudwatch_event_target" "ods_bulk_update_schedule_event" {
  rule      = aws_cloudwatch_event_rule.ods_bulk_update_schedule.name
  target_id = "ods_bulk_update_schedule_chedule"

  arn = aws_lambda_function.ods_bulk_update.arn
  depends_on = [
    aws_lambda_function.ods_bulk_update,
    aws_cloudwatch_event_rule.ods_bulk_update_schedule
  ]
}

resource "aws_lambda_permission" "bulk_upload_metadata_schedule_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ods_bulk_update.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ods_bulk_update_schedule.arn
  depends_on = [
    aws_lambda_function.ods_bulk_update,
    aws_cloudwatch_event_rule.ods_bulk_update_schedule
  ]
}