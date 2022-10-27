resource "aws_sqs_queue" "incoming_enriched_mi_events_for_s3_uploader" {
  name = "${var.environment}-gp-registrations-mi-enriched-events-queue-for-s3-lambda"

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue"
    }
  )
}