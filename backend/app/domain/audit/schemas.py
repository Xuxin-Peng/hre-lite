from datetime import datetime
from pydantic import BaseModel
from typing import Any


class AuditEventResponse(BaseModel):
    id: int
    event_id: str
    task_id: str | None
    unit_id: str | None
    event_type: str
    payload_json: dict[str, Any] | None
    created_at: datetime

    class Config:
        from_attributes = True