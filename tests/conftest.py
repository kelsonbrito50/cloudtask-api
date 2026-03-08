"""Shared test fixtures — mocked AWS services."""

import os

import boto3
import pytest
from moto import mock_aws

os.environ["TABLE_NAME"] = "test-tasks"
os.environ["QUEUE_URL"] = (
    "https://sqs.us-east-1.amazonaws.com/123456789/test-queue"
)
os.environ["TOPIC_ARN"] = (
    "arn:aws:sns:us-east-1:123456789:test-topic"
)
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"


@pytest.fixture
def aws_services():
    """Create mocked AWS services for testing."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="test-tasks",
            KeySchema=[
                {"AttributeName": "task_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "task_id", "AttributeType": "S"},
                {"AttributeName": "status", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "status-index",
                    "KeySchema": [
                        {
                            "AttributeName": "status",
                            "KeyType": "HASH",
                        },
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        sqs = boto3.client("sqs", region_name="us-east-1")
        sqs.create_queue(QueueName="test-queue")

        sns = boto3.client("sns", region_name="us-east-1")
        topic = sns.create_topic(Name="test-topic")
        os.environ["TOPIC_ARN"] = topic["TopicArn"]

        yield {
            "dynamodb": dynamodb,
            "sqs": sqs,
            "sns": sns,
            "table": dynamodb.Table("test-tasks"),
        }
