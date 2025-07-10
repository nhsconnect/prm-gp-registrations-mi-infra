resource "aws_lambda_function" "degrades_daily_summary" {
  function_name    = "${var.environment}_${var.degrades_daily_summary_lambda_name}"
  filename         = var.degrades_daily_summary_lambda_zip
  role             = aws_iam_role.degrades_daily_summary_lambda.arn
  runtime          = "python3.12"
  handler          = "main.lambda_handler"
  timeout          = 900
  source_code_hash = filebase64sha256("${var.degrades_daily_summary_lambda_zip}")
  layers           = [aws_lambda_layer_version.degrades.arn]

  environment {
    variables = {
      REGISTRATIONS_MI_EVENT_BUCKET = var.registrations_mi_event_bucket
      DEGRADES_MESSAGE_TABLE        = aws_dynamodb_table.degrades_message_table.name
      REGION                        = var.region
    }
  }
}

resource "aws_lambda_permission" "degrades_daily_summary_schedule" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.degrades_daily_summary.function_name
  principal     = "eventsa.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.degrades_daily_summary_lambda_schedule.arn
}

resource "aws_cloudwatch_event_rule" "degrades_daily_summary_lambda_schedule" {
  name                = "${var.environment}_${var.degrades_daily_summary_lambda_name}_schedule"
  description         = "Schedule for Degrades Daily Summary Lambda"
  schedule_expression = "cron(0 6 * * ? *)"
}

resource "aws_cloudwatch_event_target" "degrades_daily_summary_lambda" {
  rule      = aws_cloudwatch_event_rule.degrades_daily_summary_lambda_schedule.name
  target_id = "degrades_daily_summary_lambda_schedule"
  arn       = aws_lambda_function.degrades_daily_summary.arn
}