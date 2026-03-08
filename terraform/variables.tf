variable "project_name" {
  description = "Project name used as prefix for all resources"
  type        = string
  default     = "cloudtask"
}

variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "notification_email" {
  description = "Email for SNS task completion notifications"
  type        = string
  default     = ""
}
