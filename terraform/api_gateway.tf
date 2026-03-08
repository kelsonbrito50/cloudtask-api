# --- REST API ---
resource "aws_api_gateway_rest_api" "cloudtask" {
  name        = "cloudtask-api-${var.environment}"
  description = "Serverless Task Processing API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# --- /tasks resource ---
resource "aws_api_gateway_resource" "tasks" {
  rest_api_id = aws_api_gateway_rest_api.cloudtask.id
  parent_id   = aws_api_gateway_rest_api.cloudtask.root_resource_id
  path_part   = "tasks"
}

# --- /tasks/{id} resource ---
resource "aws_api_gateway_resource" "task_by_id" {
  rest_api_id = aws_api_gateway_rest_api.cloudtask.id
  parent_id   = aws_api_gateway_resource.tasks.id
  path_part   = "{id}"
}

# --- POST /tasks → create_task ---
resource "aws_api_gateway_method" "create_task" {
  rest_api_id      = aws_api_gateway_rest_api.cloudtask.id
  resource_id      = aws_api_gateway_resource.tasks.id
  http_method      = "POST"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "create_task" {
  rest_api_id             = aws_api_gateway_rest_api.cloudtask.id
  resource_id             = aws_api_gateway_resource.tasks.id
  http_method             = aws_api_gateway_method.create_task.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.create_task.invoke_arn
}

# --- GET /tasks → list_tasks ---
resource "aws_api_gateway_method" "list_tasks" {
  rest_api_id      = aws_api_gateway_rest_api.cloudtask.id
  resource_id      = aws_api_gateway_resource.tasks.id
  http_method      = "GET"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "list_tasks" {
  rest_api_id             = aws_api_gateway_rest_api.cloudtask.id
  resource_id             = aws_api_gateway_resource.tasks.id
  http_method             = aws_api_gateway_method.list_tasks.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.list_tasks.invoke_arn
}

# --- GET /tasks/{id} → get_task ---
resource "aws_api_gateway_method" "get_task" {
  rest_api_id      = aws_api_gateway_rest_api.cloudtask.id
  resource_id      = aws_api_gateway_resource.task_by_id.id
  http_method      = "GET"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "get_task" {
  rest_api_id             = aws_api_gateway_rest_api.cloudtask.id
  resource_id             = aws_api_gateway_resource.task_by_id.id
  http_method             = aws_api_gateway_method.get_task.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_task.invoke_arn
}

# --- PUT /tasks/{id} → update_task ---
resource "aws_api_gateway_method" "update_task" {
  rest_api_id      = aws_api_gateway_rest_api.cloudtask.id
  resource_id      = aws_api_gateway_resource.task_by_id.id
  http_method      = "PUT"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "update_task" {
  rest_api_id             = aws_api_gateway_rest_api.cloudtask.id
  resource_id             = aws_api_gateway_resource.task_by_id.id
  http_method             = aws_api_gateway_method.update_task.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_task.invoke_arn
}

# --- DELETE /tasks/{id} → delete_task ---
resource "aws_api_gateway_method" "delete_task" {
  rest_api_id      = aws_api_gateway_rest_api.cloudtask.id
  resource_id      = aws_api_gateway_resource.task_by_id.id
  http_method      = "DELETE"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "delete_task" {
  rest_api_id             = aws_api_gateway_rest_api.cloudtask.id
  resource_id             = aws_api_gateway_resource.task_by_id.id
  http_method             = aws_api_gateway_method.delete_task.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.delete_task.invoke_arn
}

# --- Lambda Permissions for API Gateway ---
resource "aws_lambda_permission" "create_task" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_task.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.cloudtask.execution_arn}/*/*"
}

resource "aws_lambda_permission" "get_task" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_task.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.cloudtask.execution_arn}/*/*"
}

resource "aws_lambda_permission" "list_tasks" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.list_tasks.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.cloudtask.execution_arn}/*/*"
}

resource "aws_lambda_permission" "update_task" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_task.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.cloudtask.execution_arn}/*/*"
}

resource "aws_lambda_permission" "delete_task" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.delete_task.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.cloudtask.execution_arn}/*/*"
}

# --- API Key + Usage Plan ---
resource "aws_api_gateway_api_key" "main" {
  name    = "cloudtask-key-${var.environment}"
  enabled = true
}

resource "aws_api_gateway_usage_plan" "main" {
  name = "cloudtask-usage-plan-${var.environment}"

  api_stages {
    api_id = aws_api_gateway_rest_api.cloudtask.id
    stage  = aws_api_gateway_stage.main.stage_name
  }

  throttle_settings {
    burst_limit = 10
    rate_limit  = 5
  }

  quota_settings {
    limit  = 1000
    period = "DAY"
  }
}

resource "aws_api_gateway_usage_plan_key" "main" {
  key_id        = aws_api_gateway_api_key.main.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.main.id
}

# --- Deployment + Stage ---
resource "aws_api_gateway_deployment" "main" {
  rest_api_id = aws_api_gateway_rest_api.cloudtask.id

  depends_on = [
    aws_api_gateway_integration.create_task,
    aws_api_gateway_integration.get_task,
    aws_api_gateway_integration.list_tasks,
    aws_api_gateway_integration.update_task,
    aws_api_gateway_integration.delete_task,
  ]

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "main" {
  deployment_id = aws_api_gateway_deployment.main.id
  rest_api_id   = aws_api_gateway_rest_api.cloudtask.id
  stage_name    = var.api_stage_name

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
  }
}

resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/cloudtask-${var.environment}"
  retention_in_days = 14
}
