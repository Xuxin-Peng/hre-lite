from typing import Any
from app.adapters.base import BaseAdapter, AdapterResult
from app.adapters.registry import register_adapter
from app.core.enums import Provider
from app.infra.db.models import RuntimeTask
from app.infra.clients.dify_client import DifyClient


@register_adapter(Provider.DIFY)
class DifyWorkflowAdapter(BaseAdapter):
    """Dify Workflow Adapter"""

    def __init__(self):
        # 不在初始化时创建 client，而是在调用时根据配置动态创建
        pass

    def _get_client(self, context: dict[str, Any]) -> DifyClient:
        """根据 context 创建 DifyClient"""
        runtime_config = context.get("runtime_config", {})
        endpoint = runtime_config.get("endpoint", "")
        api_key = runtime_config.get("api_key")
        return DifyClient(base_url=endpoint, api_key=api_key)

    async def invoke(self, task: RuntimeTask, context: dict[str, Any]) -> AdapterResult:
        """Invoke Dify workflow"""
        try:
            # Get workflow config from context
            runtime_config = context.get("runtime_config", {})
            workflow_id = runtime_config.get("workflow_id")

            if not workflow_id:
                return AdapterResult(
                    status="failed",
                    current_step=None,
                    result=None,
                    ask=None,
                    need_confirm=False,
                    error="workflow_id not configured"
                )

            # Get input payload
            inputs = task.input_payload_json or {}

            # Create client with dynamic config
            client = self._get_client(context)

            # Call Dify
            response = await client.run_workflow(
                workflow_id=workflow_id,
                inputs=inputs,
                user=task.user_id or "default-user"
            )

            # Parse response
            data = response.get("data", {})
            outputs = data.get("outputs", {})
            status = data.get("status", "succeeded")

            # Map Dify status to our status
            if status == "succeeded":
                need_confirm = outputs.get("need_confirm", False)
                return AdapterResult(
                    status="waiting_confirm" if need_confirm else "completed",
                    current_step=outputs.get("step", "completed"),
                    result=outputs,
                    ask=outputs.get("ask", "请确认是否继续") if need_confirm else None,
                    need_confirm=need_confirm,
                    error=None
                )
            elif status == "failed":
                return AdapterResult(
                    status="failed",
                    current_step=None,
                    result=None,
                    ask=None,
                    need_confirm=False,
                    error=outputs.get("error", "Workflow execution failed")
                )
            else:
                return AdapterResult(
                    status="running",
                    current_step=status,
                    result=outputs,
                    ask=None,
                    need_confirm=False,
                    error=None
                )

        except Exception as e:
            return AdapterResult(
                status="failed",
                current_step=None,
                result=None,
                ask=None,
                need_confirm=False,
                error=str(e)
            )

    async def resume(self, task: RuntimeTask, context: dict[str, Any]) -> AdapterResult:
        """Resume after confirmation"""
        try:
            runtime_config = context.get("runtime_config", {})
            workflow_id = runtime_config.get("workflow_id")

            if not workflow_id:
                return AdapterResult(
                    status="failed",
                    current_step=None,
                    result=None,
                    ask=None,
                    need_confirm=False,
                    error="workflow_id not configured"
                )

            # Get conversation_id from last output
            last_output = task.last_output_json or {}
            conversation_id = last_output.get("conversation_id", "")

            # Resume with confirmation
            inputs = {
                **task.input_payload_json,
                "confirmed": True
            }

            # Create client with dynamic config
            client = self._get_client(context)

            response = await client.resume_workflow(
                workflow_id=workflow_id,
                conversation_id=conversation_id,
                inputs=inputs,
                user=task.user_id or "default-user"
            )

            data = response.get("data", {})
            outputs = data.get("outputs", {})
            status = data.get("status", "succeeded")

            if status == "succeeded":
                return AdapterResult(
                    status="completed",
                    current_step=outputs.get("step", "completed"),
                    result=outputs,
                    ask=None,
                    need_confirm=False,
                    error=None
                )
            else:
                return AdapterResult(
                    status="failed",
                    current_step=None,
                    result=None,
                    ask=None,
                    need_confirm=False,
                    error=outputs.get("error", "Resume failed")
                )

        except Exception as e:
            return AdapterResult(
                status="failed",
                current_step=None,
                result=None,
                ask=None,
                need_confirm=False,
                error=str(e)
            )

    async def health_check(self, context: dict[str, Any] | None = None) -> bool:
        """Check Dify health"""
        # 如果有 context，使用动态配置；否则使用默认配置
        if context:
            client = self._get_client(context)
        else:
            client = DifyClient()
        return await client.health_check()