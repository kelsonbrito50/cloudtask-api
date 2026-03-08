output "api_url" {
  description = "Base URL of the CloudTask API"
  value       = aws_api_gateway_stage.main.invoke_url
}

output "api_gateway_id" {
  description = "API Gateway REST API ID"
  value       = aws_api_gateway_rest_api.cloudtask.id
}

output "tasks_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.tasks.name
}

output "tasks_table_arn" {
  description = "DynamoDB table ARN"
  value       = aws_dynamodb_table.tasks.arn
}

output "task_queue_url" {
  description = "SQS queue URL"
  value       = aws_sqs_queue.task_queue.url
}

output "dlq_url" {
  description = "Dead letter queue URL"
  value       = aws_sqs_queue.dlq.url
}

output "notification_topic_arn" {
  description = "SNS topic ARN for task notifications"
  value       = aws_sns_topic.task_notifications.arn
}

output "lambda_functions" {
  description = "Lambda function names"
  value = {
    create  = aws_lambda_function.create_task.function_name
    get     = aws_lambda_function.get_task.function_name
    list    = aws_lambda_function.list_tasks.function_name
    update  = aws_lambda_function.update_task.function_name
    delete  = aws_lambda_function.delete_task.function_name
    process = aws_lambda_function.process_task.function_name
  }
}
