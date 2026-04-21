from app.core.enums import TaskStatus
from app.core.exceptions import InvalidStateTransitionError


# Valid state transitions
VALID_TRANSITIONS = {
    TaskStatus.PENDING: [TaskStatus.RUNNING, TaskStatus.FAILED],
    TaskStatus.RUNNING: [TaskStatus.WAITING_CONFIRM, TaskStatus.COMPLETED, TaskStatus.FAILED],
    TaskStatus.WAITING_CONFIRM: [TaskStatus.RUNNING, TaskStatus.COMPLETED, TaskStatus.FAILED],
    TaskStatus.COMPLETED: [],  # Terminal state
    TaskStatus.FAILED: [TaskStatus.PENDING],  # Can reset/retry
}


def can_transition(from_status: TaskStatus, to_status: TaskStatus) -> bool:
    """Check if transition is valid"""
    return to_status in VALID_TRANSITIONS.get(from_status, [])


def validate_transition(from_status: str, to_status: str) -> None:
    """Validate transition, raise exception if invalid"""
    try:
        from_enum = TaskStatus(from_status)
        to_enum = TaskStatus(to_status)
    except ValueError as e:
        raise InvalidStateTransitionError(f"Invalid status value: {e}")

    if not can_transition(from_enum, to_enum):
        raise InvalidStateTransitionError(
            f"Cannot transition from {from_status} to {to_status}"
        )


def get_valid_transitions(status: str) -> list[str]:
    """Get valid next statuses"""
    try:
        status_enum = TaskStatus(status)
    except ValueError:
        return []
    return [s.value for s in VALID_TRANSITIONS.get(status_enum, [])]