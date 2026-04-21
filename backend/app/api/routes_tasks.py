from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.session import get_db
from app.domain.tasks.schemas import TaskCreate, TaskResponse, TaskConfirm, AdapterResultResponse
from app.domain.tasks.service import TaskService
from app.runtime.orchestrator import Orchestrator
from app.core.exceptions import TaskNotFoundError, InvalidStateTransitionError, GuardCheckFailedError

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create and execute a new RuntimeTask"""
    orchestrator = Orchestrator(db)
    try:
        task = await orchestrator.create_and_execute(
            unit_id=data.unit_id,
            user_id=data.user_id,
            session_id=data.session_id,
            input_payload=data.input_payload
        )
        # Add valid transitions
        response = TaskResponse(
            **{k: v for k, v in task.__dict__.items() if not k.startswith('_')},
            valid_transitions=orchestrator.task_service.get_valid_transitions_for_task(task.status)
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific RuntimeTask"""
    service = TaskService(db)
    try:
        task = await service.get_task(task_id)
        response = TaskResponse(
            **{k: v for k, v in task.__dict__.items() if not k.startswith('_')},
            valid_transitions=service.get_valid_transitions_for_task(task.status)
        )
        return response
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{task_id}/confirm", response_model=TaskResponse)
async def confirm_task(task_id: str, data: TaskConfirm, db: AsyncSession = Depends(get_db)):
    """Confirm and resume a RuntimeTask"""
    orchestrator = Orchestrator(db)
    try:
        task = await orchestrator.confirm_task(task_id, data.payload)
        response = TaskResponse(
            **{k: v for k, v in task.__dict__.items() if not k.startswith('_')},
            valid_transitions=orchestrator.task_service.get_valid_transitions_for_task(task.status)
        )
        return response
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except GuardCheckFailedError as e:
        raise HTTPException(status_code=400, detail=str(e))