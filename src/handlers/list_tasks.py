"""GET /tasks — List all tasks, optionally filtered by status."""

import os

import boto3

from utils.logger import get_logger
from utils.response import success

logger = get_logger(__name__)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def handler(event, context):
    """List tasks with optional status filter via query parameter."""
    params = event.get("queryStringParameters") or {}
    status_filter = params.get("status")
    limit = min(int(params.get("limit", 50)), 100)

    scan_kwargs = {"Limit": limit}

    if status_filter:
        # Use GSI for status filtering
        response = table.query(
            IndexName="status-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("status").eq(
                status_filter
            ),
            Limit=limit,
        )
    else:
        response = table.scan(**scan_kwargs)

    tasks = response.get("Items", [])
    logger.info(f"Listed {len(tasks)} tasks (filter={status_filter})")

    return success({
        "tasks": tasks,
        "count": len(tasks),
        "has_more": "LastEvaluatedKey" in response,
    })
