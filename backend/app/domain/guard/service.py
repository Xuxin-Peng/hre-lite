from app.infra.db.models import ManagedUnit, RuntimeTask, UnitRuntimeConfig
from app.core.exceptions import GuardCheckFailedError
from datetime import datetime, timedelta


class GuardService:
    """第一版最小执行控制 - 只做基础检查"""

    def check_unit_available(self, unit: ManagedUnit) -> None:
        """检查 Unit 是否可用"""
        if unit.status != "active":
            raise GuardCheckFailedError(f"Unit {unit.unit_id} is not active (status: {unit.status})")

    def check_can_confirm(self, task: RuntimeTask) -> None:
        """检查任务是否可确认"""
        if task.status != "waiting_confirm":
            raise GuardCheckFailedError(f"Task {task.task_id} is not waiting for confirmation (status: {task.status})")
        if not task.need_confirm:
            raise GuardCheckFailedError(f"Task {task.task_id} does not require confirmation")

    def check_can_resume(self, task: RuntimeTask) -> None:
        """检查任务是否可恢复执行"""
        if task.status not in ["waiting_confirm", "failed"]:
            raise GuardCheckFailedError(f"Task {task.task_id} cannot be resumed (status: {task.status})")

    def check_timeout(self, task: RuntimeTask, config: UnitRuntimeConfig | None) -> bool:
        """检查任务是否超时"""
        if not config:
            return False

        timeout_seconds = config.timeout_seconds or 300
        if task.created_at:
            elapsed = datetime.utcnow() - task.created_at
            if elapsed > timedelta(seconds=timeout_seconds):
                return True
        return False