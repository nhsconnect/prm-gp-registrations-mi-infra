variable "event_enrichment_lambda_name" {
  default = "event-enrichment-lambda"
}

resource "aws_lambda_function" "event_enrichment_lambda" {
  filename      = var.event_enrichment_lambda_zip
  function_name = "${var.environment}-${var.event_enrichment_lambda_name}"
  role          = aws_iam_role.event_enrichment_lambda_role.arn
  handler       = "main.lambda_handler"
  source_code_hash = filebase64sha256(var.event_enrichment_lambda_zip)
  runtime = "python3.9"
  timeout = 15
  tags          = local.common_tags
}

resource "aws_lambda_event_source_mapping" "sqs_queue_event_enrichment_lambda_trigger" {
  event_source_arn = aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda.arn
  function_name    = aws_lambda_function.event_enrichment_lambda.arn
}
