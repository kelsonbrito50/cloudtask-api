"""Tests for POST /tasks — create_task handler."""

import json
from unittest.mock import patch

from tests.conftest import make_event


class TestCreateTask:
    """Test suite for task creation."""

    def test_create_task_success(self):
        """Valid request creates task and returns 201."""
        event = make_event(
            method="POST",
            body={"title": "Deploy new feature", "priority": "high"},
        )

        with patch("handlers.create_task.table") as mock_table, \
             patch("handlers.create_task.sqs") as mock_sqs:
            mock_table.put_item.return_value = {}
            mock_sqs.send_message.return_value = {}

            from handlers.create_task import handler
            response = handler(event, None)

        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["title"] == "Deploy new feature"
        assert body["priority"] == "high"
        assert body["status"] == "pending"
        assert "task_id" in body
        assert "created_at" in body
        mock_table.put_item.assert_called_once()
        mock_sqs.send_message.assert_called_once()

    def test_create_task_default_priority(self):
        """Missing priority defaults to 'medium'."""
        event = make_event(method="POST", body={"title": "Simple task"})

        with patch("handlers.create_task.table") as mock_table, \
             patch("handlers.create_task.sqs") as mock_sqs:
            mock_table.put_item.return_value = {}
            mock_sqs.send_message.return_value = {}

            from handlers.create_task import handler
            response = handler(event, None)

        body = json.loads(response["body"])
        assert body["priority"] == "medium"

    def test_create_task_missing_title(self):
        """Request without title returns 400."""
        event = make_event(method="POST", body={"priority": "low"})

        from handlers.create_task import handler
        response = handler(event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "title" in body["error"].lower()

    def test_create_task_empty_body(self):
        """Empty body returns 400."""
        event = make_event(method="POST", body={})

        from handlers.create_task import handler
        response = handler(event, None)

        assert response["statusCode"] == 400

    def test_create_task_invalid_json(self):
        """Malformed JSON returns 400."""
        event = {
            "httpMethod": "POST",
            "body": "not-json{{{",
            "headers": {},
            "pathParameters": None,
            "queryStringParameters": None,
        }

        from handlers.create_task import handler
        response = handler(event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "json" in body["error"].lower()

    def test_create_task_invalid_priority(self):
        """Invalid priority value returns 400."""
        event = make_event(
            method="POST",
            body={"title": "Test", "priority": "super-urgent"},
        )

        from handlers.create_task import handler
        response = handler(event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "priority" in body["error"].lower()

    def test_create_task_sqs_message_attributes(self):
        """SQS message includes priority attribute."""
        event = make_event(
            method="POST",
            body={"title": "Critical task", "priority": "critical"},
        )

        with patch("handlers.create_task.table") as mock_table, \
             patch("handlers.create_task.sqs") as mock_sqs:
            mock_table.put_item.return_value = {}
            mock_sqs.send_message.return_value = {}

            from handlers.create_task import handler
            handler(event, None)

            call_kwargs = mock_sqs.send_message.call_args[1]
            attrs = call_kwargs["MessageAttributes"]
            assert attrs["priority"]["StringValue"] == "critical"
