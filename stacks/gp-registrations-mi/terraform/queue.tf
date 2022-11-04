resource "aws_sqs_queue" "incoming_mi_events_for_splunk_cloud_event_uploader" {
  name = "${var.environment}-gp-registrations-mi-events-queue-for-splunk-cloud-lambda"
  sqs_managed_sse_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue-for-splunk-cloud"
    }
  )
}

resource "aws_sns_topic_subscription" "incoming_mi_events_for_splunk_cloud_event_uploader" {
  protocol             = "sqs"
  raw_message_delivery = true
  topic_arn            = aws_sns_topic.mi_events.arn
  endpoint             = aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader.arn
}

resource "aws_sqs_queue" "incoming_mi_events_for_event_enrichment_lambda" {
  name = "${var.environment}-gp-registrations-mi-events-queue-for-enrichment-lambda"
  sqs_managed_sse_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue-for-enrichment"
    }
  )
}
