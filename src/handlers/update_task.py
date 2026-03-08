"""PUT /tasks/{id} — Update an existing task."""

import json
import os
from datetime import datetime, timezone

import boto3

from models.task import VALID_PRIORITIES, VALID_STATUSES
from utils.response import success, error
from utils.logger import get_logger

logger = get_logger(__name__)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

UPDATABLE_FIELDS = {"title", "description", "priority", "status"}


def handler(event, context):
    """Update task fields by task_id."""
    task_id = event.get("pathParameters", {}).get("id")

    if not task_id:
        return error("task_id is required", 400)

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return error("Invalid JSON body")

    # Filter to only updatable fields
    updates = {k: v for k, v in body.items() if k in UPDATABLE_FIELDS}

    if not updates:
        return error(f"No valid fields to update. Allowed: {', '.join(UPDATABLE_FIELDS)}")

    # Validate fields
    if "priority" in updates and updates["priority"] not in VALID_PRIORITIES:
        return error(f"priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}")

    if "status" in updates and updates["status"] not in VALID_STATUSES:
        return error(f"status must be one of: {', '.join(sorted(VALID_STATUSES))}")

    # Build update expression
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    update_expr = "SET " + ", ".join(f"#{k} = :{k}" for k in updates)
    expr_names = {f"#{k}": k for k in updates}
    expr_values = {f":{k}": v for k, v in updates.items()}

    try:
        response = table.update_item(
            Key={"task_id": task_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ConditionExpression="attribute_exists(task_id)",
            ReturnValues="ALL_NEW",
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return error("Task not found", 404)

    logger.info(f"Updated task {task_id}: {list(updates.keys())}")
    return success(response["Attributes"])
