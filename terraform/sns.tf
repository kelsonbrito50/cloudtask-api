resource "aws_sns_topic" "task_notifications" {
  name = "${var.project_name}-notifications-${var.environment}"
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.notification_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.task_notifications.arn
  protocol  = "email"
  endpoint  = var.notification_email
}
