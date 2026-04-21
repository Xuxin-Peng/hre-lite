from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from app.infra.db.models import RuntimeTask


@dataclass
class AdapterResult:
    """Unified adapter response"""
    status: str  # running, waiting_confirm, completed, failed
    current_step: str | None
    result: dict[str, Any] | None
    ask: str | None  # confirmation prompt
    need_confirm: bool
    error: str | None


class BaseAdapter(ABC):
    """Base adapter for all managed units"""

    @abstractmethod
    async def invoke(self, task: RuntimeTask, context: dict[str, Any]) -> AdapterResult:
        """Invoke the unit for the first time"""
        pass

    @abstractmethod
    async def resume(self, task: RuntimeTask, context: dict[str, Any]) -> AdapterResult:
        """Resume the unit after confirmation"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check unit health"""
        pass