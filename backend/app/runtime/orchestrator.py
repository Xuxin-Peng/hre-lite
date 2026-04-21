from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.models import ManagedUnit, UnitRuntimeConfig, RuntimeTask
from app.domain.units.service import UnitService
from app.domain.tasks.service import TaskService
from app.domain.tasks.state_machine import validate_transition
from app.domain.audit.service import AuditService
from app.domain.guard.service import GuardService
from app.adapters.registry import get_adapter
from app.runtime.context_builder import ContextBuilder
from app.core.exceptions import AdapterNotFoundError, TaskNotFoundError, UnitNotFoundError
from app.core.enums import EventType


class Orchestrator:
    """Core orchestrator for task execution"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.unit_service = UnitService(db)
        self.task_service = TaskService(db)
        self.audit_service = AuditService(db)
        self.guard = GuardService()
        self.context_builder = ContextBuilder()

    async def execute_task(self, task_id: str) -> RuntimeTask:
        """Execute a task - invoke the unit"""
        # Get task
        task = await self.task_service.get_task(task_id)

        # Get unit and config
        unit = await self.unit_service.get_unit(task.unit_id)
        config = await self.unit_service.get_runtime_config(task.unit_id)

        # Guard check
        self.guard.check_unit_available(unit)

        # Get adapter
        adapter = get_adapter(unit.provider)
        if not adapter:
            raise AdapterNotFoundError(f"No adapter for provider: {unit.provider}")

        # Build context
        context = self.context_builder.build_context(unit, config, task)

        # Update status to running
        await self.task_service.update_task_status(
            task_id=task_id,
            new_status="running"
        )

        # Log event
        await self.audit_service.log_event(
            event_type=EventType.TASK_STARTED.value,
            task_id=task_id,
            unit_id=unit.unit_id,
            payload={"input": task.input_payload_json}
        )

        # Invoke adapter
        result = await adapter.invoke(task, context)

        # Update task based on result
        updated_task = await self.task_service.update_task_status(
            task_id=task_id,
            new_status=result.status,
            current_step=result.current_step,
            last_output=result.result,
            need_confirm=result.need_confirm,
            error_message=result.error
        )

        # Log result event
        event_type = EventType.TASK_COMPLETED.value if result.status == "completed" else \
                     EventType.TASK_WAITING.value if result.status == "waiting_confirm" else \
                     EventType.TASK_FAILED.value
        await self.audit_service.log_event(
            event_type=event_type.value,
            task_id=task_id,
            unit_id=unit.unit_id,
            payload={"result": result.result, "error": result.error}
        )

        return updated_task

    async def confirm_task(self, task_id: str, confirm_payload: dict | None = None) -> RuntimeTask:
        """Confirm and resume a task"""
        # Get task
        task = await self.task_service.get_task(task_id)

        # Guard check
        self.guard.check_can_confirm(task)

        # Get unit and config
        unit = await self.unit_service.get_unit(task.unit_id)
        config = await self.unit_service.get_runtime_config(task.unit_id)

        # Get adapter
        adapter = get_adapter(unit.provider)
        if not adapter:
            raise AdapterNotFoundError(f"No adapter for provider: {unit.provider}")

        # Build resume context
        context = self.context_builder.build_resume_context(unit, config, task, confirm_payload)

        # Update status to running
        await self.task_service.update_task_status(
            task_id=task_id,
            new_status="running"
        )

        # Log confirm event
        await self.audit_service.log_event(
            event_type=EventType.TASK_CONFIRMED.value,
            task_id=task_id,
            unit_id=unit.unit_id,
            payload={"confirmed": True}
        )

        # Resume adapter
        result = await adapter.resume(task, context)

        # Update task
        updated_task = await self.task_service.update_task_status(
            task_id=task_id,
            new_status=result.status,
            current_step=result.current_step,
            last_output=result.result,
            need_confirm=result.need_confirm,
            error_message=result.error
        )

        # Log result event
        event_type = EventType.TASK_COMPLETED.value if result.status == "completed" else EventType.TASK_FAILED.value
        await self.audit_service.log_event(
            event_type=event_type.value,
            task_id=task_id,
            unit_id=unit.unit_id,
            payload={"result": result.result, "error": result.error}
        )

        return updated_task

    async def create_and_execute(self, unit_id: str, user_id: str | None, session_id: str | None, input_payload: dict) -> RuntimeTask:
        """Create a task and execute it immediately"""
        from app.domain.tasks.schemas import TaskCreate

        # Create task
        task_data = TaskCreate(
            unit_id=unit_id,
            user_id=user_id,
            session_id=session_id,
            input_payload=input_payload
        )
        task = await self.task_service.create_task(task_data)

        # Log creation
        await self.audit_service.log_event(
            event_type=EventType.TASK_CREATED.value,
            task_id=task.task_id,
            unit_id=unit_id,
            payload={"input": input_payload}
        )

        # Execute
        return await self.execute_task(task.task_id)