"""Tests for GET /tasks/{id}."""

import json

from handlers.create_task import handler as create_handler
from handlers.get_task import handler as get_handler


class TestGetTask:

    def _create(self, title="Test Task"):
        event = {"body": json.dumps({"title": title})}
        resp = create_handler(event, None)
        return json.loads(resp["body"])

    def test_get_existing(self, aws_services):
        task = self._create()
        event = {"pathParameters": {"id": task["task_id"]}}
        response = get_handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["title"] == "Test Task"

    def test_not_found(self, aws_services):
        event = {"pathParameters": {"id": "does-not-exist"}}
        response = get_handler(event, None)
        assert response["statusCode"] == 404

    def test_missing_id(self, aws_services):
        event = {"pathParameters": {}}
        response = get_handler(event, None)
        assert response["statusCode"] == 400
