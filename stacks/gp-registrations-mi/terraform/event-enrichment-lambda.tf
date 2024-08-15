variable "event_enrichment_lambda_name" {
  default = "event-enrichment-lambda"
}

resource "aws_lambda_function" "event_enrichment_lambda" {
  filename         = var.event_enrichment_lambda_zip
  function_name    = "${var.environment}-${var.event_enrichment_lambda_name}"
  role             = aws_iam_role.event_enrichment_lambda_role.arn
  handler          = "event_enrichment_main.lambda_handler"
  source_code_hash = filebase64sha256(var.event_enrichment_lambda_zip)
  runtime          = "python3.12"
  timeout          = 300
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-gp-registrations-mi"
      ApplicationRole = "AwsLambdaFunction"
    }
  )
  layers = [aws_lambda_layer_version.mi_lambda_layer.arn]
  environment {
    variables = {
      SPLUNK_CLOUD_EVENT_UPLOADER_SQS_QUEUE_URL = aws_sqs_queue.incoming_mi_events_for_splunk_cloud_event_uploader.url,
      ENRICHED_EVENTS_SNS_TOPIC_ARN             = aws_sns_topic.enriched_events_topic.arn,
      SDS_FHIR_API_KEY_PARAM_NAME               = var.sds_fhir_api_key_param_name,
      SDS_FHIR_API_URL_PARAM_NAME               = var.sds_fhir_api_url_param_name,
      GP_ODS_DYNAMO_TABLE_NAME                  = aws_dynamodb_table.mi_api_gp_ods.name,
      ICB_ODS_DYNAMO_TABLE_NAME                 = aws_dynamodb_table.mi_api_icb_ods.name,
    }
  }
}

resource "aws_lambda_event_source_mapping" "sqs_queue_event_enrichment_lambda_trigger" {
  event_source_arn = aws_sqs_queue.incoming_mi_events_for_event_enrichment_lambda.arn
  function_name    = aws_lambda_function.event_enrichment_lambda.arn
  filter_criteria {
    filter {
      pattern = jsonencode({
        body = {
          eventType : [{ "anything-but" : ["DEGRADES"] }]
        }
      })
    }
  }
}

resource "aws_cloudwatch_log_group" "event_enrichment_lambda" {
  name = "/aws/lambda/${var.environment}-${var.event_enrichment_lambda_name}"
  tags = merge(
    local.common_tags,
    {
      Name            = "${var.environment}-${var.event_enrichment_lambda_name}"
      ApplicationRole = "AwsCloudwatchLogGroup"
    }
  )
  retention_in_days = 60
}