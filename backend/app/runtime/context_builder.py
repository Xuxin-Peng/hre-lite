from typing import Any
from app.infra.db.models import ManagedUnit, UnitRuntimeConfig, RuntimeTask


class ContextBuilder:
    """Build execution context for adapters"""

    def build_context(
        self,
        unit: ManagedUnit,
        config: UnitRuntimeConfig | None,
        task: RuntimeTask
    ) -> dict[str, Any]:
        """Build context dictionary for adapter execution"""
        context = {
            "unit": {
                "unit_id": unit.unit_id,
                "name": unit.name,
                "unit_type": unit.unit_type,
                "provider": unit.provider,
                "risk_level": unit.risk_level,
            },
            "runtime_config": {},
            "task": {
                "task_id": task.task_id,
                "user_id": task.user_id,
                "session_id": task.session_id,
            },
        }

        if config:
            context["runtime_config"] = {
                "endpoint": config.endpoint,
                "api_key": config.api_key,
                "workflow_id": config.workflow_id,
                "input_mapping": config.input_mapping_json,
                "output_mapping": config.output_mapping_json,
                "confirm_policy": config.confirm_policy_json,
                "metrics_config": config.metrics_config_json,
                "timeout_seconds": config.timeout_seconds,
                "retry_limit": config.retry_limit,
            }

        return context

    def build_resume_context(
        self,
        unit: ManagedUnit,
        config: UnitRuntimeConfig | None,
        task: RuntimeTask,
        confirm_payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Build context for resume/confirm operation"""
        context = self.build_context(unit, config, task)
        context["resume"] = {
            "confirmed": True,
            "last_output": task.last_output_json,
            "confirm_payload": confirm_payload,
        }
        return context