resource "aws_cloudwatch_metric_alarm" "s3_event_uploader_lambda_dlq_alarm" {
  alarm_name          = "${var.environment}-s3-event-uploader-lambda-dlq-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"

  dimensions = {
    QueueName = aws_sqs_queue.incoming_mi_events_for_s3_event_uploader_dlq.name
  }

  alarm_description = "There is an item in the dlq that must be actioned by replaying the messages, or fixing the underlying issue. See cloudwatch logs for relevant resource for more details"

  alarm_actions = [aws_sns_topic.error_alarm_alert_topic.arn]
}

resource "aws_cloudwatch_metric_alarm" "splunk_cloud_event_uploader_lambda_dlq_alarm" {
  alarm_name          = "${var.environment}-splunk-cloud-event-uploader-lambda-dlq-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"

  dimensions = {
    QueueName = aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader_dlq.name
  }

  alarm_description = "There is an item in the dlq that must be actioned by replaying the messages, or fixing the underlying issue. See cloudwatch logs for relevant resource for more details"

  alarm_actions = [aws_sns_topic.error_alarm_alert_topic.arn]
}


resource "aws_cloudwatch_metric_alarm" "event_enrichment_lambda_dlq_alarm" {
  alarm_name          = "${var.environment}-event-enrichment-lambda-dlq-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"

  dimensions = {
    QueueName = aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda_dlq.name
  }

  alarm_description = "There is an item in the dlq that must be actioned by replaying the messages, or fixing the underlying issue. See cloudwatch logs for relevant resource for more details"

  alarm_actions = [aws_sns_topic.error_alarm_alert_topic.arn]
}

resource "aws_cloudwatch_metric_alarm" "enriched_events_sns_failure_alarm" {
  alarm_name          = "${var.environment}-enriched-events-sns-failure-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "NumberOfNotificationsFailed"
  namespace           = "AWS/SNS"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"

  dimensions = {
    TopicName = aws_sns_topic.enriched_events_topic.name
  }

  alarm_description = "There is an issue with ${aws_sns_topic.enriched_events_topic.name}. See cloudwatch logs for relevant resource for more details"

  alarm_actions = [aws_sns_topic.error_alarm_alert_topic.arn]
}
