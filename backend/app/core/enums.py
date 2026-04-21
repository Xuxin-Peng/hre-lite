from enum import Enum


class UnitType(str, Enum):
    """第一版只支持 workflow/agent/custom"""
    WORKFLOW = "workflow"
    AGENT = "agent"
    CUSTOM = "custom"


class Provider(str, Enum):
    """第一版只支持 dify/internal/reserved"""
    DIFY = "dify"
    INTERNAL = "internal"
    RESERVED = "reserved"  # 预留给未来扩展，当前不实现


class UnitStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_CONFIRM = "waiting_confirm"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EventType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_WAITING = "task_waiting"
    TASK_CONFIRMED = "task_confirmed"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    UNIT_REGISTERED = "unit_registered"
    UNIT_UPDATED = "unit_updated"