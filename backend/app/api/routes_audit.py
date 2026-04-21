from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.infra.db.session import get_db
from app.domain.audit.service import AuditService
from app.domain.audit.schemas import AuditEventResponse

router = APIRouter(prefix="/tasks", tags=["Audit"])


@router.get("/{task_id}/audit", response_model=List[AuditEventResponse])
async def get_task_audit(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get audit events for a task"""
    service = AuditService(db)
    events = await service.get_task_audit(task_id)
    return events