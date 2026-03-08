"""API key validation utilities.

Note: API key validation is handled by API Gateway's built-in
api_key_required setting. This module provides additional
validation helpers if needed for custom auth flows.
"""


def validate_api_key(event: dict) -> bool:
    """Check if the request has a valid API key header.

    In production, API Gateway handles this via usage plans.
    This is a fallback for local testing or custom validation.
    """
    headers = event.get("headers", {}) or {}
    api_key = headers.get("x-api-key") or headers.get("X-Api-Key")
    return api_key is not None and len(api_key) > 0
