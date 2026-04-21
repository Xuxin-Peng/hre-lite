from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.models import AuditEvent


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_event(self, event: AuditEvent) -> AuditEvent:
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_events_by_task(self, task_id: str) -> list[AuditEvent]:
        result = await self.db.execute(
            select(AuditEvent)
            .where(AuditEvent.task_id == task_id)
            .order_by(AuditEvent.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_events_by_unit(self, unit_id: str, limit: int = 100) -> list[AuditEvent]:
        result = await self.db.execute(
            select(AuditEvent)
            .where(AuditEvent.unit_id == unit_id)
            .order_by(AuditEvent.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())