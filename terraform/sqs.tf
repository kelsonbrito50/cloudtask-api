# --- Dead Letter Queue (failed messages land here) ---
resource "aws_sqs_queue" "dlq" {
  name                      = "cloudtask-dlq-${var.environment}"
  message_retention_seconds = 1209600 # 14 days

  tags = {
    Name = "cloudtask-dlq"
  }
}

# --- Main Task Queue ---
resource "aws_sqs_queue" "task_queue" {
  name                       = "cloudtask-queue-${var.environment}"
  visibility_timeout_seconds = 60
  message_retention_seconds  = 86400 # 1 day
  receive_wait_time_seconds  = 10    # Long polling

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name = "cloudtask-queue"
  }
}

# --- DLQ Redrive Allow Policy ---
resource "aws_sqs_queue_redrive_allow_policy" "dlq" {
  queue_url = aws_sqs_queue.dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns   = [aws_sqs_queue.task_queue.arn]
  })
}
