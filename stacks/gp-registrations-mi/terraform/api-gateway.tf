resource "aws_api_gateway_vpc_link" "vpc_link" {
  name        = "${var.environment}-gp-registrations-mi-api-gateway-vpc-link"
  description = "API Gateway VPC link that links NLB and MI API Gateway"
  target_arns = [aws_lb.nlb.arn]
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-api-gateway-vpc-link"
    }
  )
}

resource "aws_api_gateway_rest_api" "rest_api" {
  name        = "${var.environment}-gp-registrations-mi-api-gateway-rest-api"
  description = "GP Registration MI API gateway (REST API)"
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-api-gateway-rest-api"
    }
  )
}

resource "aws_api_gateway_resource" "resource" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id   = aws_api_gateway_rest_api.rest_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "method" {
  rest_api_id        = aws_api_gateway_rest_api.rest_api.id
  resource_id        = aws_api_gateway_resource.resource.id
  http_method        = "ANY"
  authorization      = "NONE"
  request_parameters = { "method.request.path.proxy" = true }
  api_key_required   = true
}

resource "aws_api_gateway_integration" "api_gateway_integration" {
  rest_api_id             = aws_api_gateway_rest_api.rest_api.id
  resource_id             = aws_api_gateway_resource.resource.id
  http_method             = aws_api_gateway_method.method.http_method
  type                    = "HTTP_PROXY"
  uri                     = format("%s/{proxy}", "http://${aws_lb.nlb.dns_name}:80")
  integration_http_method = "ANY"
  connection_type         = "VPC_LINK"
  connection_id           = aws_api_gateway_vpc_link.vpc_link.id

  cache_key_parameters = ["method.request.path.proxy"]

  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
  }
}

resource "aws_api_gateway_deployment" "api_gateway_deployment" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  stage_name  = local.api_stage_name
  depends_on = [
    aws_api_gateway_integration.api_gateway_integration,
    aws_cloudwatch_log_group.execution_logs,
    aws_cloudwatch_log_group.access_logs,
    aws_api_gateway_method.method
  ]

  triggers = {
    redeployment = sha1(join(",", tolist([
      jsonencode(aws_api_gateway_rest_api.rest_api.body),
      jsonencode(aws_api_gateway_resource.resource),
      jsonencode(aws_api_gateway_method.method),
      jsonencode(aws_api_gateway_integration.api_gateway_integration),
      jsonencode(aws_api_gateway_rest_api_policy.api_policy)
    ])))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "api_gateway_stage" {
  depends_on    = [aws_cloudwatch_log_group.access_logs, aws_cloudwatch_log_group.execution_logs]
  deployment_id = aws_api_gateway_deployment.api_gateway_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  stage_name    = local.api_stage_name

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.access_logs.arn
    format = jsonencode(
      {
        "requestId" : "$context.requestId",
        "ip" : "$context.identity.sourceIp",
        "caller" : "$context.identity.caller",
        "user" : "$context.identity.user",
        "requestTime" : "$context.requestTime",
        "httpMethod" : "$context.httpMethod",
        "resourcePath" : "$context.resourcePath",
        "status" : "$context.status",
        "protocol" : "$context.protocol",
        "responseLength" : "$context.responseLength"
      }
    )
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-api-gateway-stage"
    }
  )
}

resource "aws_api_gateway_method_settings" "method_settings" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  stage_name  = aws_api_gateway_stage.api_gateway_stage.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }
}

resource "aws_cloudwatch_log_group" "access_logs" {
  name              = "/api-gateway/${var.environment}-gp-registrations-mi/${aws_api_gateway_rest_api.rest_api.id}/${local.api_stage_name}/access"
  retention_in_days = var.retention_period_in_days

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi"
    }
  )
}

resource "aws_cloudwatch_log_group" "execution_logs" {
  name              = "/api-gateway/${var.environment}-gp-registrations-mi/${aws_api_gateway_rest_api.rest_api.id}/${local.api_stage_name}/execution"
  retention_in_days = var.retention_period_in_days

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi"
    }
  )
}

resource "aws_api_gateway_usage_plan" "api_gateway_usage_plan" {
  name         = "${var.environment}-gp-registrations-mi-api-gateway-usage-plan-api-key"
  description  = "Usage plan to configure api key to connect to the apigee proxy"

  api_stages {
    api_id = aws_api_gateway_rest_api.rest_api.id
    stage  = aws_api_gateway_stage.api_gateway_stage.stage_name
  }
}

resource "aws_api_gateway_api_key" "apigee_proxy" {
  name = "${var.environment}-gp-registrations-mi-apigee-proxy-api-key"
}

resource "aws_api_gateway_usage_plan_key" "main" {
  key_id        = aws_api_gateway_api_key.apigee_proxy.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.api_gateway_usage_plan.id
}