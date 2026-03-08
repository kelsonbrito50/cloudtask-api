"""Task model with validation."""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional
import uuid


VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_STATUSES = {"pending", "processing", "completed", "failed"}


@dataclass
class Task:
    """Represents a task in the system."""

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    priority: str = "medium"
    status: str = "pending"
    result: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def validate(self) -> list[str]:
        """Validate task fields. Returns list of error messages."""
        errors = []

        if not self.title or not self.title.strip():
            errors.append("title is required")

        if len(self.title) > 500:
            errors.append("title must be 500 characters or less")

        if self.priority not in VALID_PRIORITIES:
            errors.append(
                f"priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}"
            )

        if self.status not in VALID_STATUSES:
            errors.append(
                f"status must be one of: {', '.join(sorted(VALID_STATUSES))}"
            )

        return errors

    def to_dict(self) -> dict:
        """Convert to dictionary for DynamoDB."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create Task from dictionary."""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)
