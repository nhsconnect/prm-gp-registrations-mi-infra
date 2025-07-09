variable "degrades_message_receiver_lambda_zip" {
  type        = string
  description = "File path Degrades Message Receiver Lambda"
  default     = "./lambda/build/degrades-message-receiver.zip"
}

variable "degrades_daily_summary_lambda_zip" {
  type        = string
  description = "File path to Degrades Daily Summary Lambda"
  default     = "./lambda/build/degrades-daily-summary.zip"
}

variable "degrades_lambda_layer_zip" {
  type        = string
  description = "File path for Degrades Lambda Layer"
  default     = "./lambda/build/degrades-lambda-layer.zip"
}

variable "environment" {
  type        = string
  description = "Uniquely identities each deployment, i.e. dev, prod."
}

variable "region" {
  type        = string
  description = "AWS region to deploy to"
}

variable "degrades_message_receiver_lambda_name" {
  type        = string
  description = "Name of Degrades Message Receiver Lambda"
  default     = "degrades_message_receiver_lambda"
}

variable "degrades_daily_summary_lambda_name" {
  type        = string
  description = "Name of degrades daily summary lambda"
  default     = "degrades_daily_summary_lambda"
}

variable "registrations_mi_event_bucket" {
  type        = string
  description = "Name of GP2GP messages bucket"
}

variable "degrades_message_table" {
  type        = string
  description = "Name of Degrades Message DynamoDB table"
}

variable "degrades_message_queue" {
  type        = string
  description = "Name of Degrades Message SQS queue"
}