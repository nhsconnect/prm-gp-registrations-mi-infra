variable "splunk_cloud_event_uploader_lambda_name" {
  default = "splunk-cloud-event-uploader-lambda"
}

resource "aws_lambda_function" "splunk_cloud_event_uploader_lambda" {
  filename         = var.splunk_cloud_event_uploader_lambda_zip
  function_name    = "${var.environment}-${var.splunk_cloud_event_uploader_lambda_name}"
  role             = aws_iam_role.splunk_cloud_event_uploader_lambda_role.arn
  handler          = "splunk_cloud_event_uploader_main.lambda_handler"
  source_code_hash = filebase64sha256(var.splunk_cloud_event_uploader_lambda_zip)
  runtime          = "python3.12"
  timeout          = 15
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-${var.splunk_cloud_event_uploader_lambda_name}"
      ApplicationRole = "AwsLambdaFunction"
    }
  )

  environment {
    variables = {
      SPLUNK_CLOUD_API_TOKEN = var.splunk_cloud_api_token_param_name,
      SPLUNK_CLOUD_URL       = var.splunk_cloud_url_param_name
    }
  }
}

resource "aws_lambda_event_source_mapping" "sqs_queue_splunk_cloud_event_uploader_lambda_trigger" {
  event_source_arn = aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader.arn
  function_name    = aws_lambda_function.splunk_cloud_event_uploader_lambda.arn
}

resource "aws_cloudwatch_log_group" "splunk_cloud_event_uploader_lambda" {
  name = "/aws/lambda/${var.environment}-${var.splunk_cloud_event_uploader_lambda_name}"
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-${var.splunk_cloud_event_uploader_lambda_name}"
      ApplicationRole = "AwsCloudwatchLogGroup"
    }
  )
  retention_in_days = 60
}
