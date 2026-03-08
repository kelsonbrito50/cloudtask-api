"""DELETE /tasks/{id} — Delete a task."""

import os

import boto3

from utils.logger import log_event
from utils.response import error, success


def handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    task_id = event.get("pathParameters", {}).get("id")
    if not task_id:
        return error("Task ID is required", 400)

    response = table.get_item(Key={"task_id": task_id})
    if "Item" not in response:
        return error("Task not found", 404)

    table.delete_item(Key={"task_id": task_id})
    log_event("task_deleted", {"task_id": task_id})

    return success({"message": f"Task {task_id} deleted"})
