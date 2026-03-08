"""Tests for GET /tasks."""

import json

from handlers.create_task import handler as create_handler
from handlers.list_tasks import handler as list_handler


class TestListTasks:

    def _create(self, title="Task", priority="medium"):
        event = {
            "body": json.dumps({
                "title": title,
                "priority": priority,
            })
        }
        create_handler(event, None)

    def test_empty(self, aws_services):
        event = {"queryStringParameters": None}
        response = list_handler(event, None)
        body = json.loads(response["body"])
        assert body["count"] == 0
        assert body["tasks"] == []

    def test_multiple(self, aws_services):
        self._create("Task 1")
        self._create("Task 2")
        self._create("Task 3")

        event = {"queryStringParameters": None}
        response = list_handler(event, None)
        body = json.loads(response["body"])
        assert body["count"] == 3

    def test_filter_by_status(self, aws_services):
        self._create("Pending task")

        event = {"queryStringParameters": {"status": "pending"}}
        response = list_handler(event, None)
        body = json.loads(response["body"])
        assert body["count"] == 1
        assert body["tasks"][0]["status"] == "pending"

    def test_filter_no_matches(self, aws_services):
        self._create("Pending task")

        event = {"queryStringParameters": {"status": "completed"}}
        response = list_handler(event, None)
        body = json.loads(response["body"])
        assert body["count"] == 0
