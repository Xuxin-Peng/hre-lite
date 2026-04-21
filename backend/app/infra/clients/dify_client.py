import httpx
from typing import Any
from app.core.config import settings


class DifyClient:
    """Dify API Client"""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        mock_mode: bool | None = None
    ):
        # 支持动态传入配置，否则使用全局 settings
        self.base_url = base_url or settings.DIFY_API_URL
        self.api_key = api_key or settings.DIFY_API_KEY
        self.mock_mode = mock_mode if mock_mode is not None else settings.DIFY_MOCK_MODE

    async def run_workflow(
        self,
        workflow_id: str,
        inputs: dict[str, Any],
        user: str = "default-user"
    ) -> dict[str, Any]:
        """Run a Dify workflow"""
        if self.mock_mode:
            return self._mock_run_workflow(workflow_id, inputs)

        url = f"{self.base_url}/v1/workflows/run"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": user
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=300.0)
            response.raise_for_status()
            return response.json()

    async def resume_workflow(
        self,
        workflow_id: str,
        conversation_id: str,
        inputs: dict[str, Any],
        user: str = "default-user"
    ) -> dict[str, Any]:
        """Resume a Dify workflow (for confirmation flows)"""
        if self.mock_mode:
            return self._mock_resume_workflow(workflow_id, conversation_id, inputs)

        url = f"{self.base_url}/v1/workflows/run"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": user,
            "conversation_id": conversation_id
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=300.0)
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> bool:
        """Check Dify API health"""
        if self.mock_mode:
            return True

        try:
            url = f"{self.base_url}/health"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False

    def _mock_run_workflow(self, workflow_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
        """Mock response for development"""
        return {
            "workflow_run_id": f"mock-run-{workflow_id}",
            "task_id": f"mock-task-{workflow_id}",
            "data": {
                "id": f"mock-id-{workflow_id}",
                "workflow_id": workflow_id,
                "status": "succeeded",
                "outputs": {
                    "result": f"Mock result for {workflow_id}",
                    "need_confirm": False
                },
                "elapsed_time": 1.5
            }
        }

    def _mock_resume_workflow(self, workflow_id: str, conversation_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
        """Mock response for resume"""
        return {
            "workflow_run_id": f"mock-resume-{workflow_id}",
            "task_id": f"mock-task-resume-{workflow_id}",
            "data": {
                "id": f"mock-resume-id-{workflow_id}",
                "workflow_id": workflow_id,
                "status": "succeeded",
                "outputs": {
                    "result": f"Mock resume result for {workflow_id}",
                    "need_confirm": False
                },
                "elapsed_time": 0.8
            }
        }