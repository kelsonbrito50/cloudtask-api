"""POST /tasks — Create a new task and queue it for processing."""

import json
import os
import uuid
from datetime import datetime, timezone

import boto3

from utils.logger import log_event
from utils.response import error, success

VALID_PRIORITIES = {"low", "medium", "high", "critical"}


def handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    sqs = boto3.client("sqs")
    table = dynamodb.Table(os.environ["TABLE_NAME"])
    queue_url = os.environ["QUEUE_URL"]

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return error("Invalid JSON in request body")

    title = body.get("title", "").strip()
    if not title:
        return error("'title' is required")

    if len(title) > 200:
        return error("'title' must be 200 characters or less")

    priority = body.get("priority", "medium").lower()
    if priority not in VALID_PRIORITIES:
        valid = ", ".join(sorted(VALID_PRIORITIES))
        return error(f"'priority' must be one of: {valid}")

    description = body.get("description", "").strip()

    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    task = {
        "task_id": task_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
    }

    table.put_item(Item=task)
    log_event("task_created", {"task_id": task_id})

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({"task_id": task_id}),
        MessageAttributes={
            "priority": {
                "StringValue": priority,
                "DataType": "String",
            }
        },
    )
    log_event("task_queued", {"task_id": task_id})

    return success(task, status_code=201)
