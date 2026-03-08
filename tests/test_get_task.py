"""Tests for GET /tasks/{id} — get_task handler."""

import json
from unittest.mock import patch

from tests.conftest import make_event


class TestGetTask:
    """Test suite for single task retrieval."""

    def test_get_task_success(self):
        """Existing task returns 200 with task data."""
        event = make_event(path_params={"id": "abc-123"})

        mock_item = {
            "task_id": "abc-123",
            "title": "Test task",
            "status": "pending",
        }

        with patch("handlers.get_task.table") as mock_table:
            mock_table.get_item.return_value = {"Item": mock_item}

            from handlers.get_task import handler
            response = handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["task_id"] == "abc-123"
        assert body["title"] == "Test task"

    def test_get_task_not_found(self):
        """Non-existent task returns 404."""
        event = make_event(path_params={"id": "nonexistent"})

        with patch("handlers.get_task.table") as mock_table:
            mock_table.get_item.return_value = {}

            from handlers.get_task import handler
            response = handler(event, None)

        assert response["statusCode"] == 404

    def test_get_task_missing_id(self):
        """Missing path parameter returns 400."""
        event = make_event(path_params={})

        from handlers.get_task import handler
        response = handler(event, None)

        assert response["statusCode"] == 400
