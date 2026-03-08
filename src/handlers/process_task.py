"""SQS Consumer — Process queued tasks asynchronously."""

import json
import os
from datetime import datetime, timezone

import boto3

from utils.logger import get_logger

logger = get_logger(__name__)

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")
table = dynamodb.Table(os.environ["TABLE_NAME"])
topic_arn = os.environ["TOPIC_ARN"]


def handler(event, context):
    """Process each SQS message (batch of up to 5 tasks)."""
    failed_ids = []

    for record in event.get("Records", []):
        try:
            message = json.loads(record["body"])
            task_id = message["task_id"]
            logger.info(f"Processing task {task_id}")

            # Fetch task from DynamoDB
            response = table.get_item(Key={"task_id": task_id})
            task = response.get("Item")

            if not task:
                logger.warning(f"Task {task_id} not found, skipping")
                continue

            # Update status to processing
            table.update_item(
                Key={"task_id": task_id},
                UpdateExpression="SET #s = :s, #u = :u",
                ExpressionAttributeNames={"#s": "status", "#u": "updated_at"},
                ExpressionAttributeValues={
                    ":s": "processing",
                    ":u": datetime.now(timezone.utc).isoformat(),
                },
            )

            # ── Task processing logic ──
            # Replace this with actual business logic:
            # - Generate reports
            # - Call external APIs
            # - Run computations
            # - Process file uploads
            result = f"Processed: {task['title']} (priority: {task.get('priority', 'medium')})"

            # Update status to completed
            table.update_item(
                Key={"task_id": task_id},
                UpdateExpression="SET #s = :s, #r = :r, #u = :u",
                ExpressionAttributeNames={
                    "#s": "status",
                    "#r": "result",
                    "#u": "updated_at",
                },
                ExpressionAttributeValues={
                    ":s": "completed",
                    ":r": result,
                    ":u": datetime.now(timezone.utc).isoformat(),
                },
            )

            # Send completion notification via SNS
            sns.publish(
                TopicArn=topic_arn,
                Subject=f"Task completed: {task['title']}",
                Message=json.dumps({
                    "task_id": task_id,
                    "title": task["title"],
                    "status": "completed",
                    "result": result,
                }, default=str),
            )

            logger.info(f"Completed task {task_id}")

        except Exception as e:
            task_id = json.loads(record["body"]).get("task_id", "unknown")
            logger.error(f"Failed to process task {task_id}: {str(e)}")
            failed_ids.append(record["messageId"])

    # Report partial batch failures for SQS retry
    if failed_ids:
        return {
            "batchItemFailures": [
                {"itemIdentifier": mid} for mid in failed_ids
            ]
        }

    return {"batchItemFailures": []}
