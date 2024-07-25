resource "aws_lambda_function" "ods_bulk_update" {
  filename         = "${path.cwd}/${var.ods_bulk_update_lambda_name}"
  function_name    = "${var.environment}-${var.ods_bulk_update_lambda_name}"
  role             = aws_iam_role.bulk_ods_lambda_role.arn
  handler          = "ods_bulk_update.lambda_handler"
  source_code_hash = filebase64sha256("${path.cwd}/${var.bulk_ods_update_lambda_zip}")
  runtime          = "python3.12"
  timeout          = 300
  environment {
    variables = {
      TRUD_API_KEY_PARAM_NAME               = data.aws_ssm_parameter.trud_api_key,
      TRUD_FHIR_API_URL_PARAM_NAME          = data.aws_ssm_parameter.trud_api_endpoint,
    }
  }
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-mi-ods_bulk"
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

data "aws_ssm_parameter" "trud_api_key" {
  name = "TRUD_api_secret_key"
}

data "aws_ssm_parameter" "trud_api_endpoint" {
  name = "TRUD_api_download_endoint"
}