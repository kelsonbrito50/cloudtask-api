data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/lambda.zip"
}

# --- CRUD Lambdas ---

resource "aws_lambda_function" "create_task" {
  function_name    = "${var.project_name}-create-${var.environment}"
  role             = aws_iam_role.api_lambda.arn
  handler          = "handlers.create_task.handler"
  runtime          = "python3.12"
  timeout          = 10
  memory_size      = 128
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
      QUEUE_URL  = aws_sqs_queue.task_queue.url
    }
  }
}

resource "aws_lambda_function" "get_task" {
  function_name    = "${var.project_name}-get-${var.environment}"
  role             = aws_iam_role.api_lambda.arn
  handler          = "handlers.get_task.handler"
  runtime          = "python3.12"
  timeout          = 10
  memory_size      = 128
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}

resource "aws_lambda_function" "list_tasks" {
  function_name    = "${var.project_name}-list-${var.environment}"
  role             = aws_iam_role.api_lambda.arn
  handler          = "handlers.list_tasks.handler"
  runtime          = "python3.12"
  timeout          = 10
  memory_size      = 128
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}

resource "aws_lambda_function" "update_task" {
  function_name    = "${var.project_name}-update-${var.environment}"
  role             = aws_iam_role.api_lambda.arn
  handler          = "handlers.update_task.handler"
  runtime          = "python3.12"
  timeout          = 10
  memory_size      = 128
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}

resource "aws_lambda_function" "delete_task" {
  function_name    = "${var.project_name}-delete-${var.environment}"
  role             = aws_iam_role.api_lambda.arn
  handler          = "handlers.delete_task.handler"
  runtime          = "python3.12"
  timeout          = 10
  memory_size      = 128
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}

# --- Worker Lambda ---

resource "aws_lambda_function" "process_task" {
  function_name    = "${var.project_name}-worker-${var.environment}"
  role             = aws_iam_role.worker_lambda.arn
  handler          = "handlers.process_task.handler"
  runtime          = "python3.12"
  timeout          = 30
  memory_size      = 128
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
      TOPIC_ARN  = aws_sns_topic.task_notifications.arn
    }
  }
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.task_queue.arn
  function_name    = aws_lambda_function.process_task.arn
  batch_size       = 5
  enabled          = true
}
