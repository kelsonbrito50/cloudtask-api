"""Tests for GET /tasks — list_tasks handler."""

import json
from unittest.mock import patch

from tests.conftest import make_event


class TestListTasks:
    """Test suite for task listing."""

    def test_list_tasks_empty(self):
        """Empty table returns empty list."""
        event = make_event()

        with patch("handlers.list_tasks.table") as mock_table:
            mock_table.scan.return_value = {"Items": []}

            from handlers.list_tasks import handler
            response = handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["tasks"] == []
        assert body["count"] == 0

    def test_list_tasks_with_results(self):
        """Returns all tasks."""
        event = make_event()
        items = [
            {"task_id": "1", "title": "A", "status": "pending"},
            {"task_id": "2", "title": "B", "status": "completed"},
        ]

        with patch("handlers.list_tasks.table") as mock_table:
            mock_table.scan.return_value = {"Items": items}

            from handlers.list_tasks import handler
            response = handler(event, None)

        body = json.loads(response["body"])
        assert body["count"] == 2

    def test_list_tasks_with_status_filter(self):
        """Filters by status using GSI."""
        event = make_event(query_params={"status": "pending"})

        with patch("handlers.list_tasks.table") as mock_table:
            mock_table.query.return_value = {
                "Items": [{"task_id": "1", "status": "pending"}]
            }

            from handlers.list_tasks import handler
            response = handler(event, None)

        body = json.loads(response["body"])
        assert body["count"] == 1
        mock_table.query.assert_called_once()
