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

resource "aws_sqs_queue" "incoming_mi_events_for_event_enrichment_lambda_dlq" {
  # rename after preprod to include lambda
  name = "${var.environment}-gp-registrations-mi-events-queue-for-enrichment-dlq"
  sqs_managed_sse_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue-for-enrichment-dlq"
    }
  )
}
