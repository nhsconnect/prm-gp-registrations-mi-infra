variable "splunk_cloud_event_uploader_lambda_name" {
  default = "splunk-cloud-event-uploader-lambda"
}

resource "aws_lambda_function" "splunk_cloud_event_uploader_lambda" {
  filename      = var.splunk_cloud_event_uploader_zip
  function_name = "${var.environment}-${var.splunk_cloud_event_uploader_lambda_name}"
  role          = aws_iam_role.splunk_cloud_event_uploader_lambda_role.arn
  handler       = "main.lambda_handler"
  source_code_hash = filebase64sha256(var.splunk_cloud_event_uploader_zip)
  runtime = "python3.9"
  timeout = 15
  tags          = local.common_tags
}

resource "aws_lambda_event_source_mapping" "sqs_queue_splunk_cloud_event_uploader_lambda_trigger" {
  event_source_arn = aws_sqs_queue.incoming_enriched_mi_events_for_splunk_cloud_event_uploader.arn
  function_name    = aws_lambda_function.splunk_cloud_event_uploader_lambda.arn
}
