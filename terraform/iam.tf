# --- Lambda Execution Role ---
resource "aws_iam_role" "lambda_exec" {
  name = "cloudtask-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# --- CloudWatch Logs Policy ---
resource "aws_iam_role_policy" "lambda_logs" {
  name = "cloudtask-lambda-logs"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      Resource = "arn:aws:logs:${var.aws_region}:*:*"
    }]
  })
}

# --- DynamoDB Access (least privilege) ---
resource "aws_iam_role_policy" "dynamodb_access" {
  name = "cloudtask-dynamodb-access"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem"
        ]
        Resource = [
          aws_dynamodb_table.tasks.arn,
          "${aws_dynamodb_table.tasks.arn}/index/*"
        ]
      }
    ]
  })
}

# --- SQS Access ---
resource "aws_iam_role_policy" "sqs_access" {
  name = "cloudtask-sqs-access"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [
          aws_sqs_queue.task_queue.arn,
          aws_sqs_queue.dlq.arn
        ]
      }
    ]
  })
}

# --- SNS Publish ---
resource "aws_iam_role_policy" "sns_publish" {
  name = "cloudtask-sns-publish"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "sns:Publish"
      Resource = aws_sns_topic.task_notifications.arn
    }]
  })
}
