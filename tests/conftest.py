"""Shared test fixtures — mocked AWS services via moto."""

import json
import pytest
import boto3
from moto import mock_aws


@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    """Set required environment variables for all tests."""
    monkeypatch.setenv("TABLE_NAME", "test-tasks")
    monkeypatch.setenv("QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/123456789/test-queue")
    monkeypatch.setenv("TOPIC_ARN", "arn:aws:sns:us-east-1:123456789:test-topic")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")


@pytest.fixture
def dynamodb_table():
    """Create a mocked DynamoDB table."""
    with mock_aws():
        client = boto3.resource("dynamodb", region_name="us-east-1")
        table = client.create_table(
            TableName="test-tasks",
            KeySchema=[{"AttributeName": "task_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "task_id", "AttributeType": "S"},
                {"AttributeName": "status", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[{
                "IndexName": "status-index",
                "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            }],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        yield table


@pytest.fixture
def sqs_queue():
    """Create a mocked SQS queue."""
    with mock_aws():
        client = boto3.client("sqs", region_name="us-east-1")
        response = client.create_queue(QueueName="test-queue")
        yield response["QueueUrl"]


@pytest.fixture
def sns_topic():
    """Create a mocked SNS topic."""
    with mock_aws():
        client = boto3.client("sns", region_name="us-east-1")
        response = client.create_topic(Name="test-topic")
        yield response["TopicArn"]


def make_event(method="GET", path="/tasks", body=None, path_params=None, query_params=None):
    """Helper to create API Gateway proxy event."""
    event = {
        "httpMethod": method,
        "path": path,
        "headers": {"Content-Type": "application/json"},
        "pathParameters": path_params,
        "queryStringParameters": query_params,
        "body": json.dumps(body) if body else None,
    }
    return event
