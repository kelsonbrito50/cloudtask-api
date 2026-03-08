"""SQS Worker — Processes queued tasks asynchronously."""

import json
import os
from datetime import datetime, timezone

import boto3

from utils.logger import log_event


def handler(event, context):
    """Process each SQS message (batch of up to 5)."""
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ["TABLE_NAME"])
    sns = boto3.client("sns")
    topic_arn = os.environ["TOPIC_ARN"]

    for record in event.get("Records", []):
        try:
            message = json.loads(record["body"])
            task_id = message["task_id"]
            log_event("processing_started", {"task_id": task_id})

            response = table.get_item(Key={"task_id": task_id})
            task = response.get("Item")

            if not task:
                log_event("task_not_found", {"task_id": task_id})
                continue

            now = datetime.now(timezone.utc).isoformat()

            table.update_item(
                Key={"task_id": task_id},
                UpdateExpression="SET #s = :s, updated_at = :u",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":s": "processing",
                    ":u": now,
                },
            )

            priority = task.get("priority", "medium")
            result = (
                f"Processed task: {task['title']} "
                f"(priority: {priority})"
            )

            now = datetime.now(timezone.utc).isoformat()
            table.update_item(
                Key={"task_id": task_id},
                UpdateExpression=(
                    "SET #s = :s, #r = :r, "
                    "completed_at = :c, updated_at = :u"
                ),
                ExpressionAttributeNames={
                    "#s": "status",
                    "#r": "result",
                },
                ExpressionAttributeValues={
                    ":s": "completed",
                    ":r": result,
                    ":c": now,
                    ":u": now,
                },
            )

            sns.publish(
                TopicArn=topic_arn,
                Subject=f"Task Completed: {task['title']}",
                Message=json.dumps(
                    {
                        "task_id": task_id,
                        "title": task["title"],
                        "status": "completed",
                        "result": result,
                    },
                    indent=2,
                ),
            )

            log_event(
                "processing_completed", {"task_id": task_id}
            )

        except Exception as e:
            tid = message.get("task_id", "unknown")
            log_event("processing_failed", {
                "task_id": tid,
                "error": str(e),
            })
            raise
