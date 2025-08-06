resource "aws_cloudwatch_metric_alarm" "degrades_dlq_new_message" {
  alarm_name          = "degrades_dlq_message_alarm_${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Alarm for when there are new messages on the Degrades Message DLQ"

  dimensions = {
    QueueName = aws_sqs_queue.degrades_messages_deadletter.name
  }
}


resource "aws_cloudwatch_metric_alarm" "degrades_daily_summary_lambda_error" {
  alarm_name          = "degrades_daily_summary_lambda_error_alarm_${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  namespace           = "AWS/Lambda"
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Alarm for when degrades daily summary lambda errors"
  period              = 300
  metric_name         = "Errors"
  dimensions = {
    FunctionName = aws_lambda_function.degrades_daily_summary.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "degrades_daily_summary_lambda_duration" {
  alarm_name        = "degrades_daily_summary_lambda_duration_alarm_${var.environment}"
  alarm_description = "Triggers when duration of degrades daily summary lambda exceeds 80% of timeout."
  dimensions = {
    FunctionName = aws_lambda_function.degrades_daily_summary.function_name
  }
  threshold           = aws_lambda_function.degrades_daily_summary.timeout * 0.8 * 1000
  namespace           = "AWS/Lambda"
  metric_name         = "Duration"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  period              = "300"
  evaluation_periods  = "1"
  statistic           = "Maximum"
}

resource "aws_cloudwatch_metric_alarm" "degrades_daily_summary_lambda_memory" {
  alarm_name        = "degrades_daily_summary_lambda_memory_alarm_${var.environment}"
  alarm_description = "Triggers when max memory usage of degrades daily summary lambda exceeds 80% of provisioned memory."
  dimensions = {
    function_name = aws_lambda_function.degrades_daily_summary.function_name
  }
  threshold           = 80
  namespace           = "LambdaInsights"
  metric_name         = "memory_utilization"
  comparison_operator = "GreaterThanThreshold"
  period              = "300"
  evaluation_periods  = "1"
  statistic           = "Maximum"
}
