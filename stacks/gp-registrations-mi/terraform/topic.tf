resource "aws_sns_topic" "enriched_events_topic" {
  name = "${var.environment}-${var.enriched_mi_events_sns_topic_name}"
  kms_master_key_id = "alias/aws/sns"

  sqs_failure_feedback_role_arn = aws_iam_role.sns_topic_enriched_mi_events_cloudwatch_log_access_role.arn
  sqs_success_feedback_role_arn = aws_iam_role.sns_topic_enriched_mi_events_cloudwatch_log_access_role.arn


  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-enriched-events-sns-topic"
      ApplicationRole = "AwsSnsTopic"
    }
  )
}

resource "aws_sns_topic" "error_alarm_alert_topic" {
  name = "${var.environment}-error-alarm-alert-sns-topic"

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-error-alarm-alert-topic"
      ApplicationRole = "AwsSnsTopic"
    }
  )
}

#SQS
resource "aws_sns_topic_subscription" "enriched_events_to_s3_event_uploader_sqs_target" {
  topic_arn = aws_sns_topic.enriched_events_topic.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.incoming_mi_events_for_s3_event_uploader.arn
}

resource "aws_sns_topic_subscription" "enriched_events_to_splunk_cloud_event_uploader_sqs_target" {
  topic_arn = aws_sns_topic.enriched_events_topic.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader.arn
}

#Lambda
resource "aws_sns_topic_subscription" "error_alarm_alert_lambda_target" {
  topic_arn = aws_sns_topic.error_alarm_alert_topic.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.error_alarm_alert_lambda.arn
}
