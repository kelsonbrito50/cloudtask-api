"""Tests for POST /tasks."""

import json

from handlers.create_task import handler


class TestCreateTask:

    def test_success(self, aws_services):
        event = {
            "body": json.dumps({
                "title": "Deploy v2",
                "priority": "high",
            })
        }
        response = handler(event, None)

        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["title"] == "Deploy v2"
        assert body["priority"] == "high"
        assert body["status"] == "pending"
        assert "task_id" in body
        assert "created_at" in body

    def test_default_priority(self, aws_services):
        event = {"body": json.dumps({"title": "Fix bug"})}
        response = handler(event, None)
        body = json.loads(response["body"])
        assert body["priority"] == "medium"

    def test_missing_title(self, aws_services):
        event = {"body": json.dumps({"priority": "low"})}
        response = handler(event, None)
        assert response["statusCode"] == 400

    def test_empty_title(self, aws_services):
        event = {"body": json.dumps({"title": "   "})}
        response = handler(event, None)
        assert response["statusCode"] == 400

    def test_title_too_long(self, aws_services):
        event = {"body": json.dumps({"title": "x" * 201})}
        response = handler(event, None)
        assert response["statusCode"] == 400

    def test_invalid_priority(self, aws_services):
        event = {
            "body": json.dumps({
                "title": "Test",
                "priority": "urgent",
            })
        }
        response = handler(event, None)
        assert response["statusCode"] == 400

    def test_invalid_json(self, aws_services):
        event = {"body": "not json"}
        response = handler(event, None)
        assert response["statusCode"] == 400

    def test_empty_body(self, aws_services):
        event = {"body": "{}"}
        response = handler(event, None)
        assert response["statusCode"] == 400

    def test_with_description(self, aws_services):
        event = {
            "body": json.dumps({
                "title": "Migrate DB",
                "description": "Move to PostgreSQL",
            })
        }
        response = handler(event, None)
        body = json.loads(response["body"])
        assert body["description"] == "Move to PostgreSQL"

    def test_saved_to_dynamodb(self, aws_services):
        event = {"body": json.dumps({"title": "Persist test"})}
        response = handler(event, None)
        body = json.loads(response["body"])

        item = aws_services["table"].get_item(
            Key={"task_id": body["task_id"]}
        )
        assert item["Item"]["title"] == "Persist test"
