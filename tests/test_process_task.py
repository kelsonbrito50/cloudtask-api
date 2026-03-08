"""Tests for SQS consumer — process_task handler."""

import json
from unittest.mock import patch, MagicMock


class TestProcessTask:
    """Test suite for async task processing."""

    def _make_sqs_event(self, task_ids):
        """Helper to create SQS event with task messages."""
        return {
            "Records": [
                {
                    "messageId": f"msg-{tid}",
                    "body": json.dumps({"task_id": tid}),
                }
                for tid in task_ids
            ]
        }

    def test_process_single_task(self):
        """Successfully processes one task."""
        event = self._make_sqs_event(["task-001"])

        mock_task = {
            "task_id": "task-001",
            "title": "Build feature",
            "priority": "high",
            "status": "pending",
        }

        with patch("handlers.process_task.table") as mock_table, \
             patch("handlers.process_task.sns") as mock_sns:
            mock_table.get_item.return_value = {"Item": mock_task}
            mock_table.update_item.return_value = {}
            mock_sns.publish.return_value = {}

            from handlers.process_task import handler
            result = handler(event, None)

        assert result["batchItemFailures"] == []
        assert mock_table.update_item.call_count == 2  # processing + completed
        mock_sns.publish.assert_called_once()

    def test_process_missing_task(self):
        """Skips tasks not found in DynamoDB."""
        event = self._make_sqs_event(["ghost-task"])

        with patch("handlers.process_task.table") as mock_table, \
             patch("handlers.process_task.sns") as mock_sns:
            mock_table.get_item.return_value = {}

            from handlers.process_task import handler
            result = handler(event, None)

        assert result["batchItemFailures"] == []
        mock_table.update_item.assert_not_called()
        mock_sns.publish.assert_not_called()

    def test_process_batch(self):
        """Processes multiple tasks in a batch."""
        event = self._make_sqs_event(["t1", "t2", "t3"])

        def mock_get_item(**kwargs):
            tid = kwargs["Key"]["task_id"]
            return {"Item": {"task_id": tid, "title": f"Task {tid}", "priority": "medium"}}

        with patch("handlers.process_task.table") as mock_table, \
             patch("handlers.process_task.sns") as mock_sns:
            mock_table.get_item.side_effect = mock_get_item
            mock_table.update_item.return_value = {}
            mock_sns.publish.return_value = {}

            from handlers.process_task import handler
            result = handler(event, None)

        assert result["batchItemFailures"] == []
        assert mock_sns.publish.call_count == 3

    def test_process_partial_failure(self):
        """Reports failed messages for SQS retry."""
        event = self._make_sqs_event(["good-task", "bad-task"])

        def mock_get_item(**kwargs):
            tid = kwargs["Key"]["task_id"]
            if tid == "bad-task":
                raise Exception("Simulated failure")
            return {"Item": {"task_id": tid, "title": "Good", "priority": "low"}}

        with patch("handlers.process_task.table") as mock_table, \
             patch("handlers.process_task.sns") as mock_sns:
            mock_table.get_item.side_effect = mock_get_item
            mock_table.update_item.return_value = {}
            mock_sns.publish.return_value = {}

            from handlers.process_task import handler
            result = handler(event, None)

        failed = result["batchItemFailures"]
        assert len(failed) == 1
        assert failed[0]["itemIdentifier"] == "msg-bad-task"
