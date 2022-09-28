
data "aws_ssm_parameter" "gp_registrations_mi_repository_url" {
  name = var.gp_registrations_mi_repo_param_name
}

data "aws_ssm_parameter" "cloud_watch_log_group" {
  name = var.log_group_param_name
}

data "aws_ssm_parameter" "execution_role_arn" {
  name = var.execution_role_arn_param_name
}

data "aws_region" "current" {}

locals {
  container_name = "mi-api"
}

data "aws_ssm_parameter" "splunk_cloud_url_param_name" {
  name = var.splunk_cloud_url_param_name
}

data "aws_ssm_parameter" "splunk_cloud_api_token_param_name" {
  name = var.splunk_cloud_api_token_param_name
}

resource "aws_ecs_task_definition" "gp_registrations_mi" {
  family = "${var.environment}-${local.container_name}"

  container_definitions = jsonencode([
    {
      name      = local.container_name
      image     = "${data.aws_ssm_parameter.gp_registrations_mi_repository_url.value}:${var.gp_registrations_mi_image_tag}"
      essential = true
      environment = [
        { "name" : "OUTPUT_MI_EVENTS_BUCKET", "value" : aws_s3_bucket.mi_output.bucket },
        { "name" : "SPLUNK_CLOUD_URL", "value" : data.aws_ssm_parameter.splunk_cloud_url_param_name.value },
        { "name" : "SPLUNK_CLOUD_API_TOKEN", "value" : data.aws_ssm_parameter.splunk_cloud_api_token_param_name.value },
      ]
      portMappings = [{
        containerPort = 8080
        hostPort      = 8080
      }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = data.aws_ssm_parameter.cloud_watch_log_group.value
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "gp-registrations-mi/${var.gp_registrations_mi_image_tag}"
        }
      }
    },
  ])
  cpu                      = 1024
  memory                   = 8192
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi"
    }
  )
  execution_role_arn = data.aws_ssm_parameter.execution_role_arn.value
  task_role_arn      = aws_iam_role.gp_registrations_mi.arn
}
