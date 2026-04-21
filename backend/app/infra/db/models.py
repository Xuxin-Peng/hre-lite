from datetime import datetime
from sqlalchemy import String, Text, JSON, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infra.db.base import Base


class ManagedUnit(Base):
    __tablename__ = "managed_units"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    unit_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_type: Mapped[str] = mapped_column(String(50))
    provider: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="active")
    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), default="low")
    config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    runtime_config: Mapped["UnitRuntimeConfig | None"] = relationship(
        "UnitRuntimeConfig", back_populates="unit", uselist=False
    )


class UnitRuntimeConfig(Base):
    """工作流配置 / 生产配置"""
    __tablename__ = "unit_runtime_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    unit_id: Mapped[str] = mapped_column(String(100), ForeignKey("managed_units.unit_id"), unique=True, index=True)
    endpoint: Mapped[str] = mapped_column(String(500))
    api_key: Mapped[str | None] = mapped_column(String(200), nullable=True)
    workflow_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_mapping_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_mapping_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confirm_policy_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metrics_config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=300)
    retry_limit: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    unit: Mapped["ManagedUnit"] = relationship("ManagedUnit", back_populates="runtime_config")


class RuntimeTask(Base):
    __tablename__ = "runtime_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    unit_id: Mapped[str] = mapped_column(String(100), ForeignKey("managed_units.unit_id"), index=True)
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    current_step: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_payload_json: Mapped[dict] = mapped_column(JSON)
    last_output_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    need_confirm: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    task_id: Mapped[str | None] = mapped_column(String(100), ForeignKey("runtime_tasks.task_id"), nullable=True, index=True)
    unit_id: Mapped[str | None] = mapped_column(String(100), ForeignKey("managed_units.unit_id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)