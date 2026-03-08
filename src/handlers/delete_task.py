"""DELETE /tasks/{id} — Delete a task."""

import os

import boto3

from utils.response import success, error
from utils.logger import get_logger

logger = get_logger(__name__)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def handler(event, context):
    """Delete a task by task_id."""
    task_id = event.get("pathParameters", {}).get("id")

    if not task_id:
        return error("task_id is required", 400)

    try:
        response = table.delete_item(
            Key={"task_id": task_id},
            ConditionExpression="attribute_exists(task_id)",
            ReturnValues="ALL_OLD",
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return error("Task not found", 404)

    logger.info(f"Deleted task {task_id}")
    return success({
        "message": "Task deleted",
        "task": response.get("Attributes", {}),
    })
