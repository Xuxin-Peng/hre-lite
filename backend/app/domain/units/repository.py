from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.models import ManagedUnit, UnitRuntimeConfig


class UnitRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_unit(self, unit: ManagedUnit) -> ManagedUnit:
        self.db.add(unit)
        await self.db.commit()
        await self.db.refresh(unit)
        return unit

    async def get_unit_by_id(self, unit_id: str) -> ManagedUnit | None:
        result = await self.db.execute(
            select(ManagedUnit).where(ManagedUnit.unit_id == unit_id)
        )
        return result.scalar_one_or_none()

    async def get_units(self, skip: int = 0, limit: int = 100) -> list[ManagedUnit]:
        result = await self.db.execute(
            select(ManagedUnit).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update_unit(self, unit: ManagedUnit) -> ManagedUnit:
        await self.db.commit()
        await self.db.refresh(unit)
        return unit


class RuntimeConfigRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_config(self, config: UnitRuntimeConfig) -> UnitRuntimeConfig:
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def get_config_by_unit_id(self, unit_id: str) -> UnitRuntimeConfig | None:
        result = await self.db.execute(
            select(UnitRuntimeConfig).where(UnitRuntimeConfig.unit_id == unit_id)
        )
        return result.scalar_one_or_none()

    async def update_config(self, config: UnitRuntimeConfig) -> UnitRuntimeConfig:
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def upsert_config(self, config: UnitRuntimeConfig) -> UnitRuntimeConfig:
        existing = await self.get_config_by_unit_id(config.unit_id)
        if existing:
            for key, value in config.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(existing, key, value)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            return await self.create_config(config)