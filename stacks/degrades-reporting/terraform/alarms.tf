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