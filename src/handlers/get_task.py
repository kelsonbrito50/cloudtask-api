"""GET /tasks/{id} — Retrieve a single task by ID."""

import os

import boto3

from utils.logger import get_logger
from utils.response import error, success

logger = get_logger(__name__)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def handler(event, context):
    """Get a task by task_id from path parameters."""
    task_id = event.get("pathParameters", {}).get("id")

    if not task_id:
        return error("task_id is required", 400)

    response = table.get_item(Key={"task_id": task_id})
    task = response.get("Item")

    if not task:
        return error("Task not found", 404)

    logger.info(f"Retrieved task {task_id}")
    return success(task)
