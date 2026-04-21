from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any


class UnitCreate(BaseModel):
    unit_id: str = Field(..., description="Unique unit identifier")
    name: str = Field(..., description="Unit name")
    description: str | None = Field(None, description="Unit description")
    unit_type: str = Field(..., description="Unit type: workflow/agent/custom (第一版)")
    provider: str = Field(..., description="Provider: dify/internal/reserved (第一版)")
    status: str = Field("active", description="Status: active/inactive/maintenance")
    owner: str | None = Field(None, description="Owner identifier")
    risk_level: str = Field("low", description="Risk level: low/medium/high")
    config_json: dict[str, Any] | None = Field(None, description="Additional config")


class UnitResponse(BaseModel):
    id: int
    unit_id: str
    name: str
    description: str | None
    unit_type: str
    provider: str
    status: str
    owner: str | None
    risk_level: str
    config_json: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RuntimeConfigCreate(BaseModel):
    """工作流配置 / 生产配置"""
    endpoint: str = Field(..., description="Dify API 地址")
    api_key: str | None = Field(None, description="Dify API Key")
    workflow_id: str | None = Field(None, description="Workflow ID")
    input_mapping_json: dict[str, Any] | None = Field(None, description="Input mapping")
    output_mapping_json: dict[str, Any] | None = Field(None, description="Output mapping")
    confirm_policy_json: dict[str, Any] | None = Field(None, description="Confirmation policy")
    metrics_config_json: dict[str, Any] | None = Field(None, description="评估指标配置")
    timeout_seconds: int = Field(300, description="Timeout in seconds")
    retry_limit: int = Field(3, description="Retry limit")


class RuntimeConfigResponse(BaseModel):
    """工作流配置 / 生产配置"""
    id: int
    unit_id: str
    endpoint: str
    api_key: str | None
    workflow_id: str | None
    input_mapping_json: dict[str, Any] | None
    output_mapping_json: dict[str, Any] | None
    confirm_policy_json: dict[str, Any] | None
    metrics_config_json: dict[str, Any] | None
    timeout_seconds: int
    retry_limit: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MetricsSummary(BaseModel):
    """平台通用统计"""
    total_tasks: int = Field(..., description="总任务数")
    completed_tasks: int = Field(..., description="已完成任务数")
    failed_tasks: int = Field(..., description="失败任务数")
    waiting_confirm_tasks: int = Field(..., description="等待确认任务数")
    completion_rate: float = Field(..., description="完成率")


class MetricsConfig(BaseModel):
    """场景指标配置"""
    builtin_metrics: list[str] = Field(
        default_factory=lambda: ["total_tasks", "completed_tasks", "failed_tasks", "waiting_confirm_tasks", "completion_rate"],
        description="内置指标列表"
    )
    custom_metrics: list[dict[str, str]] = Field(
        default_factory=list,
        description="自定义指标定义"
    )


class MetricsResponse(BaseModel):
    """评估指标响应"""
    unit_id: str = Field(..., description="Unit ID")
    unit_name: str | None = Field(None, description="Unit 名称")
    summary: MetricsSummary = Field(..., description="平台通用统计")
    metrics_config: MetricsConfig | None = Field(None, description="场景绑定的指标配置")
    custom_metric_values: dict[str, float] = Field(default_factory=dict, description="自定义指标值")