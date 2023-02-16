resource "aws_cloudwatch_metric_alarm" "s3_event_uploader_lambda_dlq_alarm" {
  alarm_name          = "${aws_sqs_queue.incoming_mi_events_for_s3_event_uploader_dlq.name}-alarm"
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

  alarm_description = "There is an item in the SQS dlq: ${aws_sqs_queue.incoming_mi_events_for_s3_event_uploader_dlq.name} that must be actioned by replaying the messages, or fixing the underlying issue. See cloudwatch logs for relevant resource to find more details."

  alarm_actions = [aws_sns_topic.error_alarm_alert_topic.arn]
}

resource "aws_cloudwatch_metric_alarm" "splunk_cloud_event_uploader_lambda_dlq_alarm" {
  alarm_name          = "${aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader_dlq.name}-alarm"
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

  alarm_description = "There is an item in the SQS dlq: ${aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader_dlq.name} that must be actioned by replaying the messages, or fixing the underlying issue. See cloudwatch logs for relevant resource to find more details."

  alarm_actions = [aws_sns_topic.error_alarm_alert_topic.arn]
}


resource "aws_cloudwatch_metric_alarm" "event_enrichment_lambda_dlq_alarm" {
  alarm_name          = "${aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda_dlq.name}-alarm"
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

  alarm_description = "There is an item in the SQS dlq: ${aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda_dlq.name} that must be actioned by replaying the messages, or fixing the underlying issue. See cloudwatch logs for relevant resource to find more details."

  alarm_actions = [aws_sns_topic.error_alarm_alert_topic.arn]
}

resource "aws_cloudwatch_metric_alarm" "enriched_events_sns_failure_alarm" {
  alarm_name          = "${aws_sns_topic.enriched_events_topic.name}-alarm"
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

  alarm_description = "There is an issue with SNS topic: ${aws_sns_topic.enriched_events_topic.name}. See cloudwatch logs for relevant resource for more details."

  alarm_actions = [aws_sns_topic.error_alarm_alert_topic.arn]
}

resource "aws_cloudwatch_metric_alarm" "event_enrichment_lambda_alarm" {
  alarm_name          = "${var.environment}-${var.event_enrichment_lambda_name}-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"

  dimensions = {
    FunctionName = "${var.environment}-${var.event_enrichment_lambda_name}"
  }

  alarm_description = "There is an issue with running a lambda. See cloudwatch logs for relevant resource for more details."

  alarm_actions = [aws_sns_topic.error_alarm_alert_topic.arn]
}

resource "aws_cloudwatch_metric_alarm" "splunk_cloud_event_uploader_lambda_alarm" {
  alarm_name          = "${var.environment}-${var.splunk_cloud_event_uploader_lambda_name}-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"

  dimensions = {
    FunctionName = "${var.environment}-${var.splunk_cloud_event_uploader_lambda_name}"
  }

  alarm_description = "There is an issue with running a lambda. See cloudwatch logs for relevant resource for more details."

  alarm_actions = [aws_sns_topic.error_alarm_alert_topic.arn]
}

resource "aws_cloudwatch_metric_alarm" "s3_event_uploader_lambda_alarm" {
  alarm_name          = "${var.environment}-${var.s3_event_uploader_lambda_name}-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"

  dimensions = {
    FunctionName = "${var.environment}-${var.s3_event_uploader_lambda_name}"
  }

  alarm_description = "There is an issue with running a lambda. See cloudwatch logs for relevant resource for more details."

  alarm_actions = [aws_sns_topic.error_alarm_alert_topic.arn]
}

