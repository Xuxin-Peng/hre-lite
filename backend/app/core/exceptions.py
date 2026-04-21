class HREError(Exception):
    """Base exception for HRE"""
    pass


class UnitNotFoundError(HREError):
    """Unit not found"""
    pass


class TaskNotFoundError(HREError):
    """Task not found"""
    pass


class InvalidStateTransitionError(HREError):
    """Invalid state transition"""
    pass


class AdapterNotFoundError(HREError):
    """Adapter not found for unit type"""
    pass


class GuardCheckFailedError(HREError):
    """Guard check failed"""
    pass