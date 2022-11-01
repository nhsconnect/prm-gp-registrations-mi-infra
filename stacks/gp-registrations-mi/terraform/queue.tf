#S3
resource "aws_sqs_queue" "incoming_enriched_mi_events_for_s3_event_uploader" {
  name = "${var.environment}-gp-registrations-mi-events-queue-for-s3-lambda"
  sqs_managed_sse_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue"
    }
  )
}

resource "aws_sns_topic_subscription" "incoming_enriched_mi_events_for_s3_event_uploader" {
  protocol             = "sqs"
  raw_message_delivery = true
  topic_arn            = aws_sns_topic.enriched_mi_events.arn
  endpoint             = aws_sqs_queue.incoming_enriched_mi_events_for_s3_event_uploader.arn
}

#Spunk Cloud
resource "aws_sqs_queue" "incoming_enriched_mi_events_for_splunk_cloud_event_uploader" {
  name = "${var.environment}-gp-registrations-mi-events-queue-for-splunk-cloud-lambda"
  sqs_managed_sse_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue"
    }
  )
}

resource "aws_sns_topic_subscription" "incoming_enriched_mi_events_for_splunk_cloud_event_uploader" {
  protocol             = "sqs"
  raw_message_delivery = true
  topic_arn            = aws_sns_topic.enriched_mi_events.arn
  endpoint             = aws_sqs_queue.incoming_enriched_mi_events_for_splunk_cloud_event_uploader.arn
}
