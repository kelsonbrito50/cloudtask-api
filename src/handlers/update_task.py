"""PUT /tasks/{id} — Update a task."""

import json
import os
from datetime import datetime, timezone

import boto3

from utils.logger import log_event
from utils.response import error, success

VALID_PRIORITIES = {"low", "medium", "high", "critical"}


def handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    task_id = event.get("pathParameters", {}).get("id")
    if not task_id:
        return error("Task ID is required", 400)

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return error("Invalid JSON in request body")

    if not body:
        return error("Request body cannot be empty")

    response = table.get_item(Key={"task_id": task_id})
    if "Item" not in response:
        return error("Task not found", 404)

    update_parts = []
    expr_values = {}
    expr_names = {}

    if "title" in body:
        title = body["title"].strip()
        if not title or len(title) > 200:
            return error("'title' must be 1-200 characters")
        update_parts.append("#t = :t")
        expr_names["#t"] = "title"
        expr_values[":t"] = title

    if "description" in body:
        update_parts.append("description = :d")
        expr_values[":d"] = body["description"].strip()

    if "priority" in body:
        priority = body["priority"].lower()
        if priority not in VALID_PRIORITIES:
            valid = ", ".join(sorted(VALID_PRIORITIES))
            return error(f"'priority' must be one of: {valid}")
        update_parts.append("priority = :p")
        expr_values[":p"] = priority

    if not update_parts:
        return error("No valid fields to update")

    update_parts.append("updated_at = :u")
    expr_values[":u"] = datetime.now(timezone.utc).isoformat()

    kwargs = {
        "Key": {"task_id": task_id},
        "UpdateExpression": "SET " + ", ".join(update_parts),
        "ExpressionAttributeValues": expr_values,
        "ReturnValues": "ALL_NEW",
    }
    if expr_names:
        kwargs["ExpressionAttributeNames"] = expr_names

    result = table.update_item(**kwargs)
    log_event("task_updated", {"task_id": task_id})
    return success(result["Attributes"])
