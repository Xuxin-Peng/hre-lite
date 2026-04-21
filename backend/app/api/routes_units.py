from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.infra.db.session import get_db
from app.domain.units.service import UnitService
from app.domain.units.schemas import (
    UnitCreate, UnitResponse, RuntimeConfigCreate, RuntimeConfigResponse,
    MetricsResponse, MetricsSummary, MetricsConfig
)
from app.domain.tasks.service import TaskService
from app.domain.tasks.schemas import TaskResponse
from app.core.exceptions import UnitNotFoundError

router = APIRouter(prefix="/units", tags=["Units"])


@router.post("", response_model=UnitResponse)
async def create_unit(data: UnitCreate, db: AsyncSession = Depends(get_db)):
    """Create a new ManagedUnit"""
    service = UnitService(db)
    try:
        unit = await service.create_unit(data)
        return unit
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[UnitResponse])
async def list_units(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all ManagedUnits"""
    service = UnitService(db)
    units = await service.list_units(skip, limit)
    return units


@router.get("/{unit_id}", response_model=UnitResponse)
async def get_unit(unit_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific ManagedUnit"""
    service = UnitService(db)
    try:
        unit = await service.get_unit(unit_id)
        return unit
    except UnitNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{unit_id}/config", response_model=RuntimeConfigResponse)
async def update_unit_config(unit_id: str, data: RuntimeConfigCreate, db: AsyncSession = Depends(get_db)):
    """Update UnitRuntimeConfig for a unit"""
    service = UnitService(db)
    try:
        config = await service.update_runtime_config(unit_id, data)
        return config
    except UnitNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{unit_id}/tasks", response_model=List[TaskResponse])
async def list_unit_tasks(
    unit_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks for a specific unit (评估展示基础)"""
    unit_service = UnitService(db)
    task_service = TaskService(db)
    try:
        # Verify unit exists
        await unit_service.get_unit(unit_id)
        tasks = await task_service.list_tasks_by_unit(unit_id, skip, limit)
        # Add valid transitions for each task
        response_tasks = []
        for task in tasks:
            task_resp = TaskResponse.model_validate(task)
            task_resp.valid_transitions = task_service.get_valid_transitions_for_task(task.status)
            response_tasks.append(task_resp)
        return response_tasks
    except UnitNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{unit_id}/metrics", response_model=MetricsResponse)
async def get_unit_metrics(unit_id: str, db: AsyncSession = Depends(get_db)):
    """获取 Unit 的执行统计和指标配置"""
    unit_service = UnitService(db)
    task_service = TaskService(db)
    try:
        # Verify unit exists and get info
        unit = await unit_service.get_unit(unit_id)
        runtime_config = await unit_service.get_runtime_config(unit_id)

        # Get task statistics (通用统计)
        stats = await task_service.get_task_statistics(unit_id)

        # Calculate completion rate
        total = stats.get("total", 0)
        completed = stats.get("completed", 0)
        completion_rate = (completed / total) if total > 0 else 0.0

        # Build summary (平台通用统计)
        summary = MetricsSummary(
            total_tasks=total,
            completed_tasks=completed,
            failed_tasks=stats.get("failed", 0),
            waiting_confirm_tasks=stats.get("waiting_confirm", 0),
            completion_rate=round(completion_rate, 4)
        )

        # Build metrics_config from runtime_config
        metrics_config = None
        if runtime_config and runtime_config.metrics_config_json:
            config_data = runtime_config.metrics_config_json
            metrics_config = MetricsConfig(
                builtin_metrics=config_data.get("builtin_metrics", [
                    "total_tasks", "completed_tasks", "failed_tasks",
                    "waiting_confirm_tasks", "completion_rate"
                ]),
                custom_metrics=config_data.get("custom_metrics", [])
            )

        # Build custom_metric_values (第一版返回 mock/placeholder 值)
        custom_metric_values = {}
        if metrics_config and metrics_config.custom_metrics:
            for metric_def in metrics_config.custom_metrics:
                key = metric_def.get("key", "")
                if key:
                    # 第一版返回 mock 值，后续可接入真实计算
                    custom_metric_values[key] = 0.0

        return MetricsResponse(
            unit_id=unit_id,
            unit_name=unit.name,
            summary=summary,
            metrics_config=metrics_config,
            custom_metric_values=custom_metric_values
        )
    except UnitNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))