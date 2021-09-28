
data "aws_ssm_parameter" "ecs_cluster_arn" {
  name = var.ecs_cluster_arn_param_name
}

data "aws_ssm_parameter" "private_subnet_ids" {
  name = var.private_subnet_ids_param_name
}

resource "aws_ecs_service" "mi_service" {
  name            = "${var.environment}-gp-registrations-mi-ecs-service"
  cluster         = data.aws_ssm_parameter.ecs_cluster_arn.value
  task_definition = aws_ecs_task_definition.gp_registrations_mi.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = split(",", data.aws_ssm_parameter.private_subnet_ids.value)
    security_groups = [aws_security_group.gp_registrations_mi_container.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.alb.arn
    container_name   = "gp-registrations-mi"
    container_port   = 8080
  }

}