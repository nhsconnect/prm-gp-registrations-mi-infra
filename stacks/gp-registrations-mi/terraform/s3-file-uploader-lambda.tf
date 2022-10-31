variable "s3_event_uploader_lambda_name" {
  default = "s3-event-uploader-lambda"
}

resource "aws_lambda_function" "s3_event_uploader_lambda" {
  filename      = var.s3_event_uploader_zip
  function_name = "${var.environment}-${var.s3_event_uploader_lambda_name}"
  role          = aws_iam_role.s3_event_uploader_lambda_role.arn
  handler       = "main.lambda_handler"
  source_code_hash = filebase64sha256(var.s3_event_uploader_zip)
  runtime = "python3.9"
  timeout = 15
  tags          = local.common_tags
}