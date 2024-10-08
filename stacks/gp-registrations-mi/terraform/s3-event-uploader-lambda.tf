variable "s3_event_uploader_lambda_name" {
  default = "s3-event-uploader-lambda"
}

resource "aws_lambda_function" "s3_event_uploader_lambda" {
  filename         = var.s3_event_uploader_lambda_zip
  function_name    = "${var.environment}-${var.s3_event_uploader_lambda_name}"
  role             = aws_iam_role.s3_event_uploader_role.arn
  handler          = "s3_event_uploader_main.lambda_handler"
  source_code_hash = filebase64sha256(var.s3_event_uploader_lambda_zip)
  runtime          = "python3.12"
  timeout          = 15
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-${var.s3_event_uploader_lambda_name}"
      ApplicationRole = "AwsLambdaFunction"
    }
  )

  environment {
    variables = {
      MI_EVENTS_OUTPUT_S3_BUCKET_NAME = aws_s3_bucket.mi_events_output.bucket
    }
  }
}

resource "aws_lambda_event_source_mapping" "sqs_queue_s3_event_uploader_lambda_trigger" {
  event_source_arn = aws_sqs_queue.incoming_mi_events_for_s3_event_uploader.arn
  function_name    = aws_lambda_function.s3_event_uploader_lambda.arn
}

resource "aws_cloudwatch_log_group" "s3_event_uploader_lambda" {
  name = "/aws/lambda/${var.environment}-${var.s3_event_uploader_lambda_name}"
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-${var.s3_event_uploader_lambda_name}"
      ApplicationRole = "AwsCloudwatchLogGroup"
    }
  )
  retention_in_days = 60
}