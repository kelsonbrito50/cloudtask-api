"""GET /tasks/{id} — Retrieve a single task by ID."""

import os

import boto3

from utils.response import error, success


def handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    task_id = event.get("pathParameters", {}).get("id")
    if not task_id:
        return error("Task ID is required", 400)

    response = table.get_item(Key={"task_id": task_id})
    task = response.get("Item")

    if not task:
        return error("Task not found", 404)

    return success(task)
