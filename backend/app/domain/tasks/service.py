from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.tasks.repository import TaskRepository
from app.domain.tasks.schemas import TaskCreate, TaskConfirm
from app.domain.tasks.state_machine import validate_transition, get_valid_transitions
from app.infra.db.models import RuntimeTask
from app.core.exceptions import TaskNotFoundError, InvalidStateTransitionError
import uuid


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)

    async def create_task(self, data: TaskCreate) -> RuntimeTask:
        task_id = f"task-{uuid.uuid4().hex[:12]}"
        task = RuntimeTask(
            task_id=task_id,
            unit_id=data.unit_id,
            user_id=data.user_id,
            session_id=data.session_id,
            status="pending",
            input_payload_json=data.input_payload,
        )
        return await self.task_repo.create_task(task)

    async def get_task(self, task_id: str) -> RuntimeTask:
        task = await self.task_repo.get_task_by_id(task_id)
        if not task:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return task

    async def update_task_status(
        self,
        task_id: str,
        new_status: str,
        current_step: str | None = None,
        last_output: dict | None = None,
        need_confirm: bool | None = None,
        error_message: str | None = None
    ) -> RuntimeTask:
        task = await self.get_task(task_id)

        # Validate transition
        validate_transition(task.status, new_status)

        return await self.task_repo.update_task_status(
            task_id=task_id,
            status=new_status,
            current_step=current_step,
            last_output=last_output,
            need_confirm=need_confirm,
            error_message=error_message
        )

    async def list_tasks_by_unit(self, unit_id: str, skip: int = 0, limit: int = 100) -> list[RuntimeTask]:
        """查询某个 Unit 下的所有任务（用于评估展示）"""
        return await self.task_repo.get_tasks_by_unit(unit_id, skip, limit)

    async def get_task_statistics(self, unit_id: str) -> dict[str, int]:
        """获取某个 Unit 的任务统计数据"""
        return await self.task_repo.count_tasks_by_unit(unit_id)

    async def can_confirm_task(self, task_id: str) -> bool:
        """Check if task can be confirmed"""
        task = await self.get_task(task_id)
        return task.status == "waiting_confirm" and task.need_confirm

    def get_valid_transitions_for_task(self, status: str) -> list[str]:
        return get_valid_transitions(status)