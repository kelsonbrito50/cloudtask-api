"""GET /tasks — List all tasks, optionally filtered by status."""

import os

import boto3
from boto3.dynamodb.conditions import Attr

from utils.response import success

VALID_STATUSES = {"pending", "processing", "completed", "failed"}


def handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    params = event.get("queryStringParameters") or {}
    status_filter = params.get("status", "").lower()

    if status_filter and status_filter in VALID_STATUSES:
        response = table.scan(
            FilterExpression=Attr("status").eq(status_filter)
        )
    else:
        response = table.scan()

    tasks = response.get("Items", [])
    tasks.sort(
        key=lambda t: t.get("created_at", ""), reverse=True
    )

    return success({"count": len(tasks), "tasks": tasks})
