# resource "aws_lb" "alb" {
#   name               = "${var.environment}-gp-registrations-mi-alb"
#   internal           = false
#   load_balancer_type = "application"
#   security_groups    = [aws_security_group.inbound_only.id]
#   subnets            = aws_subnet.public.id

#   enable_deletion_protection = true

#   tags = merge(
#     local.common_tags,
#     {
#       Name = "${var.environment}-gp-registrations-mi-alb"
#     }
#   )
# }

# resource "aws_lb_target_group" "alb" {
#   name     = "${var.environment}-gp-registrations-mi-alb-tg"
#   port     = 8080
#   protocol = "HTTP"
#   vpc_id   = aws_vpc.vpc.id
# }

# resource "aws_lb_listener" "client" {
#   load_balancer_arn = aws_lb.alb.arn
#   port              = "443"
#   protocol          = "HTTP"

#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.alb.arn
#   }
# }