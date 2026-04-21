from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.audit.repository import AuditRepository
from app.infra.db.models import AuditEvent
import uuid


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_repo = AuditRepository(db)

    async def log_event(
        self,
        event_type: str,
        task_id: str | None = None,
        unit_id: str | None = None,
        payload: dict | None = None
    ) -> AuditEvent:
        event_id = f"evt-{uuid.uuid4().hex[:12]}"
        event = AuditEvent(
            event_id=event_id,
            task_id=task_id,
            unit_id=unit_id,
            event_type=event_type,
            payload_json=payload,
        )
        return await self.audit_repo.create_event(event)

    async def get_task_audit(self, task_id: str) -> list[AuditEvent]:
        return await self.audit_repo.get_events_by_task(task_id)