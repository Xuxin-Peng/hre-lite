# HRE-lite MVP

Heterogeneous Runtime Engine - 数字值班员工作流验证场景

---

## 第一版验证目标

验证"数字值班员工作流配置 + 任务执行 + 完成情况与评估展示"的完整闭环。

---

## 核心概念说明

### ManagedUnit = 被纳管对象

代表一个被平台纳管的执行单元，如"数字值班员事件接入"工作流。

### UnitRuntimeConfig = 工作流配置 / 生产配置

代表该工作流在生产环境的具体配置，包括：
- API endpoint
- workflow_id
- 超时重试参数
- **评估指标配置 (metrics_config_json)**

数字值班员在平台上的配置，本质上是：

```
创建一个 ManagedUnit（被纳管对象）
    └给它绑定一个 UnitRuntimeConfig（工作流配置）
```

---

## 核心主链路

```
┌──────────────────┐
│  1. 注册 Unit     │  POST /units
│  (ManagedUnit)   │  创建"数字值班员事件接入"工作流单元
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│  2. 配置 Runtime │  PUT /units/{unit_id}/config
│  (UnitRuntimeConfig) │  设置 endpoint、workflow_id、metrics_config_json
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│  3. 创建 Task    │  POST /tasks
│  (RuntimeTask)   │  提交事件输入，立即执行
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│  4. 查询状态     │  GET /tasks/{task_id}
│                  │  查看任务执行状态和结果
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│  5. 查询审计     │  GET /tasks/{task_id}/audit
│  (AuditEvent)    │  查看任务完整执行记录
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│  6. 查询指标     │  GET /units/{unit_id}/metrics
│                  │  查看执行统计和评估指标
└──────────────────┘
```

---

## 快速开始

### 1. 安装依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. 访问 API 文档

- Swagger UI: http://localhost:8000/docs

---

## 数字值班员验证完整示例

### Step 1: 注册"数字值班员事件接入"工作流

```bash
curl -X POST http://localhost:8000/units \
  -H "Content-Type: application/json" \
  -d '{
    "unit_id": "duty_event_intake",
    "name": "数字值班员-事件接入",
    "description": "值班事件智能接入与分拨工作流",
    "unit_type": "workflow",
    "provider": "dify",
    "status": "active",
    "risk_level": "medium",
    "owner": "ops-team"
  }'
```

返回：

```json
{
  "id": 1,
  "unit_id": "duty_event_intake",
  "name": "数字值班员-事件接入",
  "unit_type": "workflow",
  "provider": "dify",
  "status": "active",
  "risk_level": "medium"
}
```

### Step 2: 配置工作流生产配置

```bash
curl -X PUT http://localhost:8000/units/duty_event_intake/config \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "http://your-dify-server:80",
    "api_key": "app-xxxxxxxxxxxxxx",
    "workflow_id": "wf-duty-intake-001",
    "timeout_seconds": 300,
    "retry_limit": 3,
    "metrics_config_json": {
      "builtin_metrics": [
        "total_tasks",
        "completed_tasks",
        "failed_tasks",
        "waiting_confirm_tasks",
        "completion_rate"
      ],
      "custom_metrics": [
        {
          "key": "dispatch_accept_rate",
          "name": "智能分拨采纳率",
          "type": "ratio"
        },
        {
          "key": "element_extract_accuracy",
          "name": "七要素提取准确率",
          "type": "ratio"
        }
      ]
    }
  }'
```

返回：

```json
{
  "id": 1,
  "unit_id": "duty_event_intake",
  "endpoint": "http://your-dify-server:80",
  "api_key": "app-xxxxxxxxxxxxxx",
  "workflow_id": "wf-duty-intake-001",
  "timeout_seconds": 300,
  "retry_limit": 3,
  "metrics_config_json": {
    "builtin_metrics": [...],
    "custom_metrics": [...]
  }
}
```

### Step 3: 创建任务（提交值班事件）

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "unit_id": "duty_event_intake",
    "user_id": "operator-001",
    "session_id": "session-20240115",
    "input_payload": {
      "event_text": "告警: 生产服务器node-03 CPU使用率超过90%",
      "event_source": "monitor-system",
      "event_time": "2024-01-15T10:30:00"
    }
  }'
```

返回：

```json
{
  "task_id": "task-a1b2c3d4",
  "unit_id": "duty_event_intake",
  "status": "completed",
  "current_step": "completed",
  "input_payload_json": {
    "event_text": "告警: 生产服务器node-03 CPU使用率超过90%",
    ...
  },
  "last_output_json": {
    "result": "Mock result for wf-duty-intake-001",
    "need_confirm": false
  },
  "need_confirm": false,
  "valid_transitions": []
}
```

### Step 4: 查询任务状态

```bash
curl http://localhost:8000/tasks/task-a1b2c3d4
```

### Step 5: 查询审计日志

```bash
curl http://localhost:8000/tasks/task-a1b2c3d4/audit
```

返回：

```json
[
  {
    "event_id": "evt-001",
    "task_id": "task-a1b2c3d4",
    "unit_id": "duty_event_intake",
    "event_type": "task_created",
    "payload_json": {"input": {...}},
    "created_at": "2024-01-15T10:30:00"
  },
  {
    "event_id": "evt-002",
    "event_type": "task_started",
    "payload_json": {"input": {...}},
    "created_at": "2024-01-15T10:30:01"
  },
  {
    "event_id": "evt-003",
    "event_type": "task_completed",
    "payload_json": {"result": {...}},
    "created_at": "2024-01-15T10:30:05"
  }
]
```

### Step 6: 查询执行指标

```bash
curl http://localhost:8000/units/duty_event_intake/metrics
```

返回：

```json
{
  "unit_id": "duty_event_intake",
  "unit_name": "数字值班员-事件接入",
  "summary": {
    "total_tasks": 10,
    "completed_tasks": 7,
    "failed_tasks": 1,
    "waiting_confirm_tasks": 2,
    "completion_rate": 0.7
  },
  "metrics_config": {
    "builtin_metrics": [
      "total_tasks",
      "completed_tasks",
      "failed_tasks",
      "waiting_confirm_tasks",
      "completion_rate"
    ],
    "custom_metrics": [
      {
        "key": "dispatch_accept_rate",
        "name": "智能分拨采纳率",
        "type": "ratio"
      },
      {
        "key": "element_extract_accuracy",
        "name": "七要素提取准确率",
        "type": "ratio"
      }
    ]
  },
  "custom_metric_values": {
    "dispatch_accept_rate": 0.0,
    "element_extract_accuracy": 0.0
  }
}
```

---

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /units | 创建 ManagedUnit（被纳管对象） |
| GET | /units | 列表查询 |
| GET | /units/{unit_id} | 单个查询 |
| PUT | /units/{unit_id}/config | 配置 UnitRuntimeConfig（工作流配置） |
| GET | /units/{unit_id}/tasks | 查询 Unit 下所有任务 |
| GET | /units/{unit_id}/metrics | 查询执行统计和评估指标 |
| POST | /tasks | 创建并执行任务 |
| GET | /tasks/{task_id} | 查询任务状态 |
| POST | /tasks/{task_id}/confirm | 确认/恢复任务（需确认场景） |
| GET | /tasks/{task_id}/audit | 查询审计日志 |
| GET | /health | 健康检查 |

---

## 核心对象

### ManagedUnit（被纳管对象）

代表一个被平台纳管的执行单元。

```
ManagedUnit
├── unit_id: str       # 唯一标识，如 "duty_event_intake"
├── name: str          # 名称，如 "数字值班员-事件接入"
├── unit_type: str     # workflow/agent/custom
├── provider: str      # dify（第一版）
├── status: str        # active/inactive/maintenance
├── risk_level: str    # low/medium/high
├── owner: str         # 负责人
```

### UnitRuntimeConfig（工作流配置 / 生产配置）

代表工作流在生产环境的具体配置。

```
UnitRuntimeConfig
├── unit_id: str              # 关联的 Unit
├── endpoint: str             # Dify API 地址
├── api_key: str              # Dify API Key
├── workflow_id: str          # Dify Workflow ID
├── input_mapping_json        # 输入映射（可选）
├── output_mapping_json       # 输出映射（可选）
├── confirm_policy_json       # 确认策略（可选）
├── metrics_config_json       # 评估指标配置
├── timeout_seconds: int      # 超时时间（默认 300）
├── retry_limit: int          # 重试次数（默认 3）
```

**metrics_config_json 结构**：

```json
{
  "builtin_metrics": [
    "total_tasks",
    "completed_tasks",
    "failed_tasks",
    "waiting_confirm_tasks",
    "completion_rate"
  ],
  "custom_metrics": [
    {
      "key": "dispatch_accept_rate",
      "name": "智能分拨采纳率",
      "type": "ratio"
    }
  ]
}
```

### RuntimeTask（运行时任务）

```
RuntimeTask
├── task_id: str           # 任务唯一标识
├── unit_id: str           # 执行的 Unit
├── status: str            # pending/running/waiting_confirm/completed/failed
├── input_payload_json     # 输入数据（如值班事件内容）
├── last_output_json       # 最新输出
├── need_confirm: bool     # 是否需要人工确认
├── error_message: str     # 错误信息
```

### AuditEvent（审计事件）

```
AuditEvent
├── event_id: str      # 事件唯一标识
├── task_id: str       # 关联的任务
├── unit_id: str       # 关联的 Unit
├── event_type: str    # task_created/task_started/task_completed/...
├── payload_json       # 事件详情
├── created_at         # 时间戳
```

---

## 状态流转

```
pending → running → completed/failed/waiting_confirm
waiting_confirm → running → completed/failed
failed → pending (可重试)
```

---

## /units/{unit_id}/metrics 返回结构

```json
{
  "unit_id": "duty_event_intake",
  "unit_name": "数字值班员-事件接入",
  "summary": {
    "total_tasks": 10,
    "completed_tasks": 7,
    "failed_tasks": 1,
    "waiting_confirm_tasks": 2,
    "completion_rate": 0.7
  },
  "metrics_config": {
    "builtin_metrics": [...],
    "custom_metrics": [...]
  },
  "custom_metric_values": {
    "dispatch_accept_rate": 0.62
  }
}
```

| 字段 | 说明 |
|------|------|
| summary | 平台通用统计，来自 TaskService.get_task_statistics() |
| metrics_config | 场景绑定的指标配置，来自 UnitRuntimeConfig.metrics_config_json |
| custom_metric_values | 自定义指标值，第一版返回 placeholder |

---

## Mock 模式

设置 `DIFY_MOCK_MODE=true`（默认），无需真实 Dify API，方便本地验证。

---

## 第一版边界

### 做

- Dify Workflow 纳管
- 数字值班员配置（ManagedUnit + UnitRuntimeConfig）
- 任务执行与状态流转
- 审计日志
- 指标配置与展示（summary + metrics_config + custom_metric_values）

### 不做

- 多 Agent 协同编排
- 复杂指标引擎
- 复杂权限系统
- 可视化编排界面