from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.models import RuntimeTask


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, task: RuntimeTask) -> RuntimeTask:
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_task_by_id(self, task_id: str) -> RuntimeTask | None:
        result = await self.db.execute(
            select(RuntimeTask).where(RuntimeTask.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_tasks_by_unit(self, unit_id: str, skip: int = 0, limit: int = 100) -> list[RuntimeTask]:
        result = await self.db.execute(
            select(RuntimeTask)
            .where(RuntimeTask.unit_id == unit_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_task(self, task: RuntimeTask) -> RuntimeTask:
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        current_step: str | None = None,
        last_output: dict | None = None,
        need_confirm: bool | None = None,
        error_message: str | None = None
    ) -> RuntimeTask | None:
        task = await self.get_task_by_id(task_id)
        if task:
            task.status = status
            if current_step is not None:
                task.current_step = current_step
            if last_output is not None:
                task.last_output_json = last_output
            if need_confirm is not None:
                task.need_confirm = need_confirm
            if error_message is not None:
                task.error_message = error_message
            await self.db.commit()
            await self.db.refresh(task)
        return task

    async def count_tasks_by_unit(self, unit_id: str) -> dict[str, int]:
        """统计某个 Unit 下各状态的任务数量"""
        result = await self.db.execute(
            select(RuntimeTask.status, func.count(RuntimeTask.id))
            .where(RuntimeTask.unit_id == unit_id)
            .group_by(RuntimeTask.status)
        )
        status_counts = dict(result.all())

        # 获取总任务数
        total_result = await self.db.execute(
            select(func.count(RuntimeTask.id))
            .where(RuntimeTask.unit_id == unit_id)
        )
        total = total_result.scalar() or 0

        return {
            "total": total,
            "pending": status_counts.get("pending", 0),
            "running": status_counts.get("running", 0),
            "completed": status_counts.get("completed", 0),
            "failed": status_counts.get("failed", 0),
            "waiting_confirm": status_counts.get("waiting_confirm", 0),
            "cancelled": status_counts.get("cancelled", 0),
        }