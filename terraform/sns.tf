# --- SNS Topic for Task Notifications ---
resource "aws_sns_topic" "task_notifications" {
  name = "cloudtask-notifications-${var.environment}"

  tags = {
    Name = "cloudtask-notifications"
  }
}

# --- Email Subscription (optional) ---
resource "aws_sns_topic_subscription" "email" {
  count     = var.notification_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.task_notifications.arn
  protocol  = "email"
  endpoint  = var.notification_email
}
