# Splunk cloud uploader
resource "aws_sqs_queue" "incoming_mi_events_for_splunk_cloud_event_uploader" {
  name = "${var.environment}-gp-registrations-mi-events-queue-for-splunk-cloud-lambda"
  sqs_managed_sse_enabled = true
  message_retention_seconds = 1209600

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue-for-splunk-cloud"
      ApplicationRole = "AwsSqsQueue"
    }
  )
}

resource "aws_sqs_queue" "incoming_mi_events_for_splunk_cloud_event_uploader_dlq" {
  name = "${var.environment}-gp-registrations-mi-events-queue-for-splunk-uploader-dlq"
  sqs_managed_sse_enabled = true
  message_retention_seconds = 1209600

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader_dlq.arn
    maxReceiveCount     = 10
  })

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue-for-splunk-uploader-dlq"
      ApplicationRole = "AwsSqsQueue"
    }
  )
}

resource "aws_sqs_queue_redrive_allow_policy" "incoming_mi_events_for_splunk_cloud_event_uploader_dlq_allow" {
  queue_url = aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader_dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader.arn]
  })
}

# Event enrichment lambda
resource "aws_sqs_queue" "incoming_mi_events_for_event_enrichment_lambda" {
  name = "${var.environment}-gp-registrations-mi-events-queue-for-enrichment-lambda"
  sqs_managed_sse_enabled = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda_dlq.arn
    maxReceiveCount     = 10
  })

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue-for-enrichment"
      ApplicationRole = "AwsSqsQueue"
    }
  )
}

resource "aws_sqs_queue" "incoming_mi_events_for_event_enrichment_lambda_dlq" {
  name = "${var.environment}-gp-registrations-mi-events-queue-for-enrichment-dlq"
  sqs_managed_sse_enabled = true
  message_retention_seconds = 1209600

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue-for-enrichment-dlq"
      ApplicationRole = "AwsSqsQueue"
    }
  )
}

resource "aws_sqs_queue_redrive_allow_policy" "incoming_mi_events_for_event_enrichment_lambda_dlq_allow" {
  queue_url = aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda_dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda.arn]
  })
}

# S3 uploader
resource "aws_sqs_queue" "incoming_mi_events_for_s3_event_uploader" {
  name = "${var.environment}-gp-registrations-mi-events-queue-for-s3-uploader-lambda"
  sqs_managed_sse_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue-for-s3-uploader"
      ApplicationRole = "AwsSqsQueue"
    }
  )
}

resource "aws_sqs_queue" "incoming_mi_events_for_s3_event_uploader_dlq" {
  name = "${var.environment}-gp-registrations-mi-events-queue-for-s3-uploader-dlq"
  sqs_managed_sse_enabled = true
  message_retention_seconds = 1209600

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.incoming_mi_events_for_s3_event_uploader_dlq.arn
    maxReceiveCount     = 10
  })

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-sqs-queue-for-s3-uploader-dlq"
      ApplicationRole = "AwsSqsQueue"
    }
  )
}

resource "aws_sqs_queue_redrive_allow_policy" "incoming_mi_events_for_s3_event_uploader_dlq_allow" {
  queue_url = aws_sqs_queue.incoming_mi_events_for_s3_event_uploader_dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.incoming_mi_events_for_s3_event_uploader.arn]
  })
}

