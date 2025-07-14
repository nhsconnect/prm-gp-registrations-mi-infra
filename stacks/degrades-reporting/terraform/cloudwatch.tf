resource "aws_cloudwatch_log_group" "degrades_message_receiver" {
  name              = "/aws/lambda/${aws_lambda_function.degrades_message_receiver.function_name}"
  retention_in_days = 0
}

resource "aws_cloudwatch_log_group" "degrades_daily_summary" {
  name              = "/aws/lambda/${aws_lambda_function.degrades_daily_summary.function_name}"
  retention_in_days = 0
}