resource "aws_ssm_parameter" "splunk_cloud_event_uploader_sqs_queue_url" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/splunk-cloud-event-uploader-sqs-queue-url"
  type  = "String"
  value = aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader.url
  tags  = local.common_tags
}

resource "aws_ssm_parameter" "event_enrichment_sqs_queue_url" {
  name  = "/registrations/${var.environment}/gp-registrations-mi/event-enrichment-sqs-queue-url"
  type  = "String"
  value = aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda.url
  tags  = local.common_tags
}
