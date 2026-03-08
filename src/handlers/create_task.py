"""POST /tasks — Create a new task and queue it for processing."""

import json
import os

import boto3

from models.task import Task
from utils.response import success, error
from utils.logger import get_logger

logger = get_logger(__name__)

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")
table = dynamodb.Table(os.environ["TABLE_NAME"])
queue_url = os.environ["QUEUE_URL"]


def handler(event, context):
    """Create a task, store in DynamoDB, send to SQS for processing."""
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return error("Invalid JSON body")

    # Build and validate task
    task = Task(
        title=body.get("title", ""),
        description=body.get("description", ""),
        priority=body.get("priority", "medium"),
    )

    errors = task.validate()
    if errors:
        return error("; ".join(errors))

    # Store in DynamoDB
    table.put_item(Item=task.to_dict())
    logger.info(f"Created task {task.task_id}: {task.title}")

    # Queue for async processing
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({"task_id": task.task_id}),
        MessageAttributes={
            "priority": {
                "DataType": "String",
                "StringValue": task.priority,
            }
        },
    )
    logger.info(f"Queued task {task.task_id}")

    return success(task.to_dict(), status_code=201)
