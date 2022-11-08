resource "aws_iam_role" "gp_registrations_mi" {
  name               = "${var.environment}-gp-registrations-mi"
  description        = "Role for gp registrations mi ecs service"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
  managed_policy_arns = [
    aws_iam_policy.incoming_mi_events_sns_topic_publish.arn
  ]
}

data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = [
    "sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_api_gateway_rest_api_policy" "api_policy" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  policy      = data.aws_iam_policy_document.apigee_ip_policy.json
}

data "aws_iam_policy_document" "apigee_ip_policy" {
  statement {
    sid = "AllowApigeeIps"
    actions = [
      "execute-api:Invoke"
    ]
    resources = [
      "${aws_api_gateway_rest_api.rest_api.execution_arn}/${local.api_stage_name}/POST/*"
    ]
    condition {
      test     = "IpAddress"
      values   = split(",", data.aws_ssm_parameter.apigee_ips.value)
      variable = "aws:SourceIp"
    }
    principals {
      type        = "*"
      identifiers = ["*"]
    }
  }

  statement {
    sid = "AllowGETStatus"
    actions = [
      "execute-api:Invoke"
    ]
    resources = [
      "${aws_api_gateway_rest_api.rest_api.execution_arn}/${local.api_stage_name}/GET/_status"
    ]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
  }
}

data "aws_ssm_parameter" "apigee_ips" {
  name = var.apigee_ips_param_name
}
