# --- Log Groups for each Lambda ---
resource "aws_cloudwatch_log_group" "create_task" {
  name              = "/aws/lambda/cloudtask-create-${var.environment}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "get_task" {
  name              = "/aws/lambda/cloudtask-get-${var.environment}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "list_tasks" {
  name              = "/aws/lambda/cloudtask-list-${var.environment}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "update_task" {
  name              = "/aws/lambda/cloudtask-update-${var.environment}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "delete_task" {
  name              = "/aws/lambda/cloudtask-delete-${var.environment}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "process_task" {
  name              = "/aws/lambda/cloudtask-process-${var.environment}"
  retention_in_days = 14
}

# --- Alarm: DLQ has messages (failed processing) ---
resource "aws_cloudwatch_metric_alarm" "dlq_messages" {
  alarm_name          = "cloudtask-dlq-not-empty-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Alert when dead letter queue has failed messages"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.dlq.name
  }

  alarm_actions = [aws_sns_topic.task_notifications.arn]
}

# --- Alarm: Lambda errors spike ---
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "cloudtask-lambda-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Alert when Lambda errors exceed threshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.process_task.function_name
  }

  alarm_actions = [aws_sns_topic.task_notifications.arn]
}
