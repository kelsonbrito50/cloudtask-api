# --- Package Lambda code ---
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/.build/lambda.zip"
}

# --- CRUD Lambdas ---

resource "aws_lambda_function" "create_task" {
  function_name    = "cloudtask-create-${var.environment}"
  runtime          = var.lambda_runtime
  handler          = "handlers.create_task.handler"
  role             = aws_iam_role.lambda_exec.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
      QUEUE_URL  = aws_sqs_queue.task_queue.url
      ENV        = var.environment
    }
  }

  depends_on = [aws_cloudwatch_log_group.create_task]
}

resource "aws_lambda_function" "get_task" {
  function_name    = "cloudtask-get-${var.environment}"
  runtime          = var.lambda_runtime
  handler          = "handlers.get_task.handler"
  role             = aws_iam_role.lambda_exec.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
      ENV        = var.environment
    }
  }

  depends_on = [aws_cloudwatch_log_group.get_task]
}

resource "aws_lambda_function" "list_tasks" {
  function_name    = "cloudtask-list-${var.environment}"
  runtime          = var.lambda_runtime
  handler          = "handlers.list_tasks.handler"
  role             = aws_iam_role.lambda_exec.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
      ENV        = var.environment
    }
  }

  depends_on = [aws_cloudwatch_log_group.list_tasks]
}

resource "aws_lambda_function" "update_task" {
  function_name    = "cloudtask-update-${var.environment}"
  runtime          = var.lambda_runtime
  handler          = "handlers.update_task.handler"
  role             = aws_iam_role.lambda_exec.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
      ENV        = var.environment
    }
  }

  depends_on = [aws_cloudwatch_log_group.update_task]
}

resource "aws_lambda_function" "delete_task" {
  function_name    = "cloudtask-delete-${var.environment}"
  runtime          = var.lambda_runtime
  handler          = "handlers.delete_task.handler"
  role             = aws_iam_role.lambda_exec.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
      ENV        = var.environment
    }
  }

  depends_on = [aws_cloudwatch_log_group.delete_task]
}

# --- Worker Lambda (SQS consumer) ---

resource "aws_lambda_function" "process_task" {
  function_name    = "cloudtask-process-${var.environment}"
  runtime          = var.lambda_runtime
  handler          = "handlers.process_task.handler"
  role             = aws_iam_role.lambda_exec.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 30
  memory_size      = var.lambda_memory

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
      TOPIC_ARN  = aws_sns_topic.task_notifications.arn
      ENV        = var.environment
    }
  }

  depends_on = [aws_cloudwatch_log_group.process_task]
}

# --- SQS → Lambda Trigger ---
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn                   = aws_sqs_queue.task_queue.arn
  function_name                      = aws_lambda_function.process_task.arn
  batch_size                         = 5
  maximum_batching_window_in_seconds = 10
  enabled                            = true
}
