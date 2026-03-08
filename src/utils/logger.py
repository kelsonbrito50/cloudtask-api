"""Structured logging for Lambda functions."""

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def log_event(action, data=None):
    """Log a structured event."""
    event = {"action": action}
    if data:
        event["data"] = data
    logger.info(json.dumps(event))
