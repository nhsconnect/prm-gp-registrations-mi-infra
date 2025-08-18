resource "aws_lambda_function" "ods_bulk_update" {
  filename         = var.bulk_ods_update_lambda_zip
  function_name    = "${var.environment}-${var.ods_bulk_update_lambda_name}"
  role             = aws_iam_role.bulk_ods_lambda.arn
  handler          = "bulk_ods_update.lambda_handler"
  source_code_hash = filebase64sha256(var.bulk_ods_update_lambda_zip)
  runtime          = "python3.12"
  timeout          = 300
  memory_size      = 512
  layers           = [aws_lambda_layer_version.mi_enrichment.arn]
  environment {
    variables = {
      GP_ODS_DYNAMO_TABLE_NAME  = aws_dynamodb_table.mi_api_gp_ods.name,
      ICB_ODS_DYNAMO_TABLE_NAME = aws_dynamodb_table.mi_api_icb_ods.name,
      ODS_S3_BUCKET_NAME        = aws_s3_bucket.ods_csv_files.bucket
    }
  }
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-mi-ods-bulk"
      ApplicationRole = "AwsLambdaFunction"
    }
  )
}

resource "aws_cloudwatch_log_group" "bulk_ods_update_lambda" {
  name = "/aws/lambda/${var.environment}-${var.ods_bulk_update_lambda_name}"
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-${var.ods_bulk_update_lambda_name}"
      ApplicationRole = "AwsCloudwatchLogGroup"
    }
  )
  retention_in_days = 60
}

resource "aws_cloudwatch_event_rule" "ods_bulk_update_schedule" {
  name                = "${var.environment}_ods_bulk_update_schedule"
  description         = "Schedule for ODS Update Lambda"
  schedule_expression = "cron(0 4 ? * 1 *)"
}

resource "aws_cloudwatch_event_target" "ods_bulk_update_schedule_event" {
  rule      = aws_cloudwatch_event_rule.ods_bulk_update_schedule.name
  target_id = "ods_bulk_update_schedule"

  arn = aws_lambda_function.ods_bulk_update.arn
  depends_on = [
    aws_lambda_function.ods_bulk_update,
    aws_cloudwatch_event_rule.ods_bulk_update_schedule
  ]
}

resource "aws_lambda_permission" "bulk_upload_metadata_schedule_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ods_bulk_update.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ods_bulk_update_schedule.arn
  depends_on = [
    aws_lambda_function.ods_bulk_update,
  ]
}
