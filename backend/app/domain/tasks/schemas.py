from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any


class TaskCreate(BaseModel):
    unit_id: str = Field(..., description="Unit ID to execute")
    user_id: str | None = Field(None, description="User ID")
    session_id: str | None = Field(None, description="Session ID")
    input_payload: dict[str, Any] = Field(..., description="Input payload")


class TaskResponse(BaseModel):
    id: int
    task_id: str
    unit_id: str
    user_id: str | None
    session_id: str | None
    status: str
    current_step: str | None
    input_payload_json: dict[str, Any]
    last_output_json: dict[str, Any] | None
    need_confirm: bool
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    valid_transitions: list[str] = []

    class Config:
        from_attributes = True


class TaskConfirm(BaseModel):
    confirmed: bool = Field(True, description="Whether to confirm")
    payload: dict[str, Any] | None = Field(None, description="Additional payload for resume")


class AdapterResultResponse(BaseModel):
    status: str
    current_step: str | None
    result: dict[str, Any] | None
    ask: str | None
    need_confirm: bool
    error: str | None