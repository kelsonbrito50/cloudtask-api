"""Tests for SQS Worker Lambda."""

import json

from handlers.create_task import handler as create_handler
from handlers.process_task import handler as process_handler


class TestProcessTask:

    def _create_id(self, aws_services):
        event = {
            "body": json.dumps({
                "title": "Process me",
                "priority": "high",
            })
        }
        resp = create_handler(event, None)
        return json.loads(resp["body"])["task_id"]

    def test_success(self, aws_services):
        task_id = self._create_id(aws_services)

        sqs_event = {
            "Records": [
                {"body": json.dumps({"task_id": task_id})}
            ]
        }
        process_handler(sqs_event, None)

        item = aws_services["table"].get_item(
            Key={"task_id": task_id}
        )
        assert item["Item"]["status"] == "completed"
        assert "result" in item["Item"]
        assert "completed_at" in item["Item"]

    def test_nonexistent_task(self, aws_services):
        sqs_event = {
            "Records": [
                {"body": json.dumps({"task_id": "ghost-id"})}
            ]
        }
        process_handler(sqs_event, None)

    def test_batch(self, aws_services):
        id1 = self._create_id(aws_services)
        id2 = self._create_id(aws_services)

        sqs_event = {
            "Records": [
                {"body": json.dumps({"task_id": id1})},
                {"body": json.dumps({"task_id": id2})},
            ]
        }
        process_handler(sqs_event, None)

        t1 = aws_services["table"].get_item(Key={"task_id": id1})
        t2 = aws_services["table"].get_item(Key={"task_id": id2})
        assert t1["Item"]["status"] == "completed"
        assert t2["Item"]["status"] == "completed"
