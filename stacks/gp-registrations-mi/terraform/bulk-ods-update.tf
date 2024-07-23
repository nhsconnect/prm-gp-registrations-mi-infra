variable "ods_bulk_update_lambda_name" {
  default = "ods_bulk_update_lambda"
}

resource "aws_lambda_function" "event_enrichment_lambda" {
  filename      = "${path.cwd}/${var.ods_bulk_update_lambda_name}"
  function_name = "${var.environment}-${var.ods_bulk_update_lambda_name}"
  role          = aws_iam_role.bulk_ods_lambda_role.arn
  handler       = "ods_bulk_update.lambda_handler"
  source_code_hash = filebase64sha256("${path.cwd}/${var.bulk_ods_update_lambda_zip}")
  runtime = "python3.12"
  timeout = 300
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-mi-ods_bulk"
      ApplicationRole = "AwsLambdaFunction"
    }
  )
}


resource "aws_cloudwatch_log_group" "bulk_ods_update_lambda" {
  name = "/aws/lambda/${var.environment}-${var.ods_bulk_update_lambda_name}"
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-${var.ods_bulk_update_lambda_name}"
      ApplicationRole = "AwsCloudwatchLogGroup"
    }
  )
  retention_in_days = 60
}
