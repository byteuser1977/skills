# Hermes Team Orchestration

基于 Hermes Agent 原生能力实现的多代理团队编排系统，具备任务路由、生命周期管理和质量门控功能。

## 核心能力

- **任务规划** — 将复杂需求拆解为结构化任务
- **智能路由** — 根据任务类型自动路由到最适合的代理/模型
- **生命周期管理** — Planning → Building → Reviewing → Done
- **质量门控** — 强制 review 阶段才能完成任务
- **工作区隔离** — 每个代理有独立工作区，共享 artifacts 目录

## 安装

### 方法 1: 复制到 Hermes 技能目录

```bash
mkdir -p ~/.hermes/skills/hermes-team-orchestration
cp -r /tmp/hermes-team-orchestration/* ~/.hermes/skills/hermes-team-orchestration/
```

然后 Hermes 会自动加载该技能。

### 方法 2: 直接安装工具到 Hermes tools 目录（立即可用）

```bash
mkdir -p ~/.hermes/hermes-agent/tools/
cp /tmp/hermes-team-orchestration/tools/hermes_team_orchestration_register.py \
   ~/.hermes/hermes-agent/tools/hermes_team_orchestration.py
```

重启 Hermes 会话或运行 `discover_builtin_tools()` 即可注册工具。

## 快速开始

### 1. 创建团队配置

```yaml
# .hermes-team/config.yaml
agents:
  orchestrator:
    model:
      provider: "anthropic"
      model: "claude-3-5-sonnet-latest"
    toolsets: ["file", "session_search", "plan"]
    role: "Orchestrator — 路由任务、跟踪状态、最终验收"

  builder:
    model:
      provider: "openrouter"
      model: "anthropic/claude-3.5-sonnet"
    toolsets: ["terminal", "file", "code_execution", "browser"]
    role: "Builder — 实现功能、生产 artifacts"

  reviewer:
    model:
      provider: "openrouter"
      model: "openai/gpt-4.1"
    toolsets: ["file"]
    role: "Reviewer — 代码审查、质量审计"
```

### 2. 初始化团队

```python
import hermes_team_orchestration as hto

team_config = {
    "orchestrator": {
        "model": {"provider": "anthropic", "model": "claude-3-5-sonnet-latest"},
        "toolsets": ["file", "session_search"],
        "role": "Orchestrator"
    },
    "builder": {
        "model": {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
        "toolsets": ["terminal", "file", "code_execution"],
        "role": "Builder"
    },
    "reviewer": {
        "model": {"provider": "openrouter", "model": "openai/gpt-4.1"},
        "toolsets": ["file"],
        "role": "Reviewer"
    }
}

hto.init_team(team_config, workspace="/projects/myapp")
```

这会创建：
- `/.hermes-team/config.yaml`
- `/agents/{orchestrator,builder,reviewer}/SOUL.md`
- `shared/` 目录
- `agents/` 目录

### 3. 规划复杂请求

```python
plan = hto.plan_request(
    request="Build a REST API with user authentication and rate limiting",
    agent="orchestrator",
    use_planning_skill=True  # Uses writing-plans if available
)

# plan.plan_tasks 是任务列表
for task_item in plan["plan_tasks"]:
    task = hto.create_task(
        title=task_item["title"],
        description=task_item["description"],
        category=task_item.get("category", "CODE"),
        acceptance_criteria=task_item.get("acceptance", [])
    )
    # 自动路由
    assignee = hto.route_task(task)
    hto.assign_task(task, assignee=assignee)
```

### 4. 执行与评审

```python
# 所有任务并行执行（受 max_workers 限制）
import concurrent.futures

tasks = [...]  # from planning
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    futures = [pool.submit(hto.work_task, t) for t in tasks]
    for f in concurrent.futures.as_completed(futures):
        result = f.result()
        print(f"Task {result['task_id']} completed, status: {result['status']}")

# 评审所有处于 REVIEW 状态的任务
for task in hto.list_tasks(status="REVIEW"):
    review = hto.review_task(task, reviewer="reviewer")
    if review["approved"]:
        hto.complete_task(task)
    else:
        print(f"Task {task['task_id']} needs rework: {review['feedback']}")
```

### 5. 查看状态

```python
# 所有任务
all_tasks = hto.list_tasks()

# 某个代理的待办
builder_tasks = hto.list_tasks(assignee="builder", status="IN_PROGRESS")

# 代理状态
status = hto.get_agent_status("builder")
print(status)
```

## Workspace 结构

```
/projects/myapp/
├── .hermes-team/
│   ├── config.yaml              # 团队配置
│   ├── tasks.jsonl              # 任务注册表（追加写）
│   ├── routing.json             # 路由规则（可选）
│   ├── task_abcdef12/           # 单个任务目录
│   │   ├── spec.md              # 任务规格（自动生成）
│   │   ├── artifacts/           # 输出文件（软链到 shared/）
│   │   ├── review.json          # 评审结果
│   │   └── handoff.md           # 完成时的交接说明
│   └── agents/
│       ├── orchestrator/SOUL.md
│       ├── builder/SOUL.md
│       └── reviewer/SOUL.md
├── shared/                      # 所有交付物
│   ├── docs/
│   ├── code/
│   └── manifest.json            # 艺术品注册表
└── (你的项目文件)
```

## 工具 API 参考

所有工具以 `hto_` 前缀出现在 Hermes 中（自动发现）：

| 工具名 | 说明 |
|--------|------|
| `hto_init_team` | 初始化团队工作区 |
| `hto_create_task` | 创建任务 |
| `hto_assign_task` | 分配任务给代理 |
| `hto_work_task` | 执行任务（delegate_task 封装） |
| `hto_review_task` | 评审任务 |
| `hto_complete_task` | 完成任务 |
| `hto_fail_task` | 失败任务 |
| `hto_route_task` | 智能路由 |
| `hto_list_tasks` | 列出任务 |
| `hto_get_task` | 获取任务详情 |
| `hto_get_agent_status` | 代理状态 |
| `hto_plan_request` | 规划请求 |
| `hto_on_transition` | 注册状态转换回调 |
| `hto_register_artifact` | 注册艺术品 |
| `hto_query_artifacts` | 查询艺术品 |

**注意**: 所有工具运行时需要先初始化团队（`init_team` 已调用）。

## 自定义路由规则

创建 `/.hermes-team/routing.json`：

```json
{
  "rules": [
    {
      "category": "CODE",
      "subcategory": "python",
      "preferred_agent": "backend",
      "required_tools": ["terminal", "file", "code_execution"]
    },
    {
      "category": "CODE",
      "subcategory": "frontend",
      "preferred_agent": "frontend"
    }
  ],
  "fallback": {"default_agent": "orchestrator"}
}
```

## 生命周期钩子

```python
from hermes_team_orchestration import on_transition

def send_notification(task):
    # 发送到飞书/ slack
    pass

on_transition("IN_PROGRESS", "REVIEW", send_notification)
on_transition("REVIEW", "DONE", lambda t: print(f"✅ {t['title']}"))
```

## SOUL.md 模板（代理身份）

每个代理应该有自己的 `agents/<name>/SOUL.md`：

```markdown
# Agent: builder

## Role
实现功能，产出 artifacts。

## Scope
- 编写代码、单元测试
- 配置、dockerfile
- 遵循 TDD

## Boundaries
- 不重新分配任务
- 不自行标记 DONE
- 阻塞超过 10 分钟需评论

## Handoff Format
1. Work Summary: 做了什么
2. Artifacts: 文件路径
3. Verification: 验证命令
4. Known Issues: 遗留问题
5. Next: 下一步动作

## Tools
terminal, file, code_execution
```

## Best Practices

1. 任务大小：2-5 分钟的工作量
2. 明确 artifacts：`create_task(artifacts=['shared/api/server.py'])`
3. toolset 匹配：builder 只用必要的工具
4. 模型 tier：orchestrator 和 reviewer 用 top-tier；builder 可用性价比模型
5. 强制 review：never skip review step
6. 工作区隔离：每个代理有自己的 SOUL.md
7. 交接详细：handoff 必须包含验证步骤

## 与 OpenClaw `agent-swarm` 对比

| OpenClaw 概念 | Hermes 实现 |
|---------------|-------------|
| `sessions_spawn()` | `delegate_task()` |
| `router.py` 路由 | `hto.route_task()` + `config.yaml` |
| `openclaw.json` | `config.yaml` + `routing.json` |
| 平台特定 MCP | Hermes toolsets |
| 外部会话管理 | 内置生命周期管理 |

可以直接将 OpenClaw 的 routing rules 转换为 `routing.json`。

## 故障排除

### 任务卡在 IN_PROGRESS

```bash
# 查看子代理日志（通过 Hermes history）
hto.get_task(task_id)['history']
# 强制失败
hto.fail_task(task, reason="Subagent timeout")
```

### Review 循环（一直不通过）

```python
# 紧急绕过（慎用）
# 设置更高 approval_threshold 或人工介入
hto.review_task(task, reviewer="orchestrator")
```

### 模型错误

```python
status = hto.get_agent_status("builder")
print(status['model'])
# 更新
# 编辑 config.yaml 中的 model 字段
```

## License

MIT — 自由使用、修改、部署。

---

**版本**: 1.0.0  
**更新**: 2025-04-20  
**Hermes 兼容性**: >= 2.0.0