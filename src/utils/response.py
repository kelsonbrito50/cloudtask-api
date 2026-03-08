"""Standardized API response helpers."""

import json
from typing import Any


def success(body: dict[str, Any], status_code: int = 200) -> dict:
    """Return a successful API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, default=str),
    }


def error(message: str, status_code: int = 400) -> dict:
    """Return an error API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"error": message}),
    }
