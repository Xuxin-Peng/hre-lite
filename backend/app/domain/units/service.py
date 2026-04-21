from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.units.repository import UnitRepository, RuntimeConfigRepository
from app.domain.units.schemas import UnitCreate, RuntimeConfigCreate
from app.infra.db.models import ManagedUnit, UnitRuntimeConfig
from app.core.exceptions import UnitNotFoundError
from datetime import datetime
import uuid


class UnitService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.unit_repo = UnitRepository(db)
        self.config_repo = RuntimeConfigRepository(db)

    async def create_unit(self, data: UnitCreate) -> ManagedUnit:
        unit = ManagedUnit(
            unit_id=data.unit_id,
            name=data.name,
            description=data.description,
            unit_type=data.unit_type,
            provider=data.provider,
            status=data.status,
            owner=data.owner,
            risk_level=data.risk_level,
            config_json=data.config_json,
        )
        return await self.unit_repo.create_unit(unit)

    async def get_unit(self, unit_id: str) -> ManagedUnit:
        unit = await self.unit_repo.get_unit_by_id(unit_id)
        if not unit:
            raise UnitNotFoundError(f"Unit not found: {unit_id}")
        return unit

    async def list_units(self, skip: int = 0, limit: int = 100) -> list[ManagedUnit]:
        return await self.unit_repo.get_units(skip, limit)

    async def update_runtime_config(self, unit_id: str, data: RuntimeConfigCreate) -> UnitRuntimeConfig:
        """更新 UnitRuntimeConfig - 工作流配置"""
        # Verify unit exists
        unit = await self.get_unit(unit_id)

        config = UnitRuntimeConfig(
            unit_id=unit_id,
            endpoint=data.endpoint,
            api_key=data.api_key,
            workflow_id=data.workflow_id,
            input_mapping_json=data.input_mapping_json,
            output_mapping_json=data.output_mapping_json,
            confirm_policy_json=data.confirm_policy_json,
            metrics_config_json=data.metrics_config_json,
            timeout_seconds=data.timeout_seconds,
            retry_limit=data.retry_limit,
        )
        return await self.config_repo.upsert_config(config)

    async def get_runtime_config(self, unit_id: str) -> UnitRuntimeConfig | None:
        return await self.config_repo.get_config_by_unit_id(unit_id)