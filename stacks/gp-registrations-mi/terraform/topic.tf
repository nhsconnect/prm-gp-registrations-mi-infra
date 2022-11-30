resource "aws_sns_topic" "enriched_events_topic" {
  name = "gp-registrations-mi-enriched-events-sns-topic"
  kms_master_key_id = "alias/aws/sns"

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-gp-registrations-mi-enriched-events-sns-topic"
    }
  )
}