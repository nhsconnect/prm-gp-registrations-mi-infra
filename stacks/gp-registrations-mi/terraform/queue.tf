resource "aws_sqs_queue" "incoming_enriched_mi_events_for_s3_uploader" {
  name = "${var.environment}-gp-registrations-mi-enriched-events-queue-for-s3-lambda"

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue"
    }
  )
}

resource "aws_sns_topic_subscription" "incoming_enriched_mi_events_for_s3_uploader" {
  protocol             = "sqs"
  raw_message_delivery = true
  topic_arn            = aws_sns_topic.enriched_mi_events.arn
  endpoint             = aws_sqs_queue.incoming_enriched_mi_events_for_s3_uploader.arn
}

