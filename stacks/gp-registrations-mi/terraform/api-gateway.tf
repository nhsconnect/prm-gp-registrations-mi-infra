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
  stage_name  = "${var.environment}-env"
  depends_on = [aws_api_gateway_integration.api_gateway_integration,
  aws_cloudwatch_log_group.api_gateway_stage, aws_api_gateway_account.api_gateway, aws_api_gateway_method.method]

  triggers = {
    redeployment = sha1(join(",", tolist([
      jsonencode(aws_api_gateway_rest_api.rest_api.body),
      jsonencode(aws_api_gateway_resource.resource),
      jsonencode(aws_api_gateway_method.method),
      jsonencode(aws_api_gateway_integration.api_gateway_integration)
    ])))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "api_gateway_stage" {
  depends_on    = [aws_cloudwatch_log_group.api_gateway_stage]
  deployment_id = aws_api_gateway_deployment.api_gateway_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  stage_name    = "${var.environment}-env"

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

resource "aws_cloudwatch_log_group" "api_gateway_stage" {
  name              = "/api-gateway/${var.environment}-gp-registrations-mi/${aws_api_gateway_rest_api.rest_api.id}/${var.environment}-env"
  retention_in_days = 7

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi"
    }
  )
}

resource "aws_api_gateway_account" "api_gateway" {
  cloudwatch_role_arn = aws_iam_role.cloudwatch_role.arn
}

data "aws_iam_policy_document" "assume_iam_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"
      identifiers = [
        "apigateway.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "cloudwatch_role" {
  name               = "${var.environment}-gp-registrations-mi-api-gateway"
  description        = "API gateway role to allow for cloudwatch logging"
  assume_role_policy = data.aws_iam_policy_document.assume_iam_role.json
}

data "aws_iam_policy_document" "cloudwatch_iam_policy" {
  statement {
    sid = "CloudwatchLogs"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents",
      "logs:GetLogEvents",
      "logs:FilterLogEvents"
    ]
    resources = [
      "*"
    ]
  }
}

resource "aws_iam_role_policy" "cloudwatch_role_policy" {
  name   = "${var.environment}-api-gateway-cloudwatch-log"
  role   = aws_iam_role.cloudwatch_role.id
  policy = data.aws_iam_policy_document.cloudwatch_iam_policy.json
}
