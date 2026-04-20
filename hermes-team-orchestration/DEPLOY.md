# 安装与部署指南

## 方式一：自动安装（推荐）

```bash
# 1. 下载或克隆此项目到本地
# 假设技能包在 ~/downloads/hermes-team-orchestration

# 2. 运行安装脚本
cd ~/downloads/hermes-team-orchestration
chmod +x install.sh
./install.sh

# 3. 重启 Hermes 会话或重新加载工具
# Hermes 会自动发现 ~/.hermes/hermes-agent/tools/ 下的工具
```

安装脚本会：
- 复制技能包到 `~/.hermes/skills/hermes-team-orchestration/`
- 在 `~/.hermes/hermes-agent/tools/` 创建注册链接
- Hermes 重启后，工具自动注册为 `hto_*` 前缀

## 方式二：手动复制

```bash
# 复制整个技能目录
cp -r hermes-team-orchestration ~/.hermes/skills/

# 复制注册器到 tools 目录（软链或硬链）
ln -s ~/.hermes/skills/hermes-team-orchestration/tools/hermes_team_orchestration_register.py \
       ~/.hermes/hermes-agent/tools/hermes_team_orchestration.py

# 重启 Hermes（或 reload tools）
```

## 验证安装

在 Hermes CLI 中：

```python
# 列出现有工具
tools_list = list_tools()
# 应该看到 hermes-team 前缀的工具

# 或调用一个工具测试
result = hto_get_agent_status(agent="orchestrator")  # 但这时还没有初始化团队
# 会返回 Error: team not initialized
```

## 初始化您的项目

### 1. 准备团队配置

创建目录结构：

```bash
cd /path/to/your/project
mkdir -p .hermes-team
cp ~/.hermes/skills/hermes-team-orchestration/config.yaml.template .hermes-team/config.yaml
```

编辑 `config.yaml`，定义您的团队：

```yaml
agents:
  # 调度者：负责规划、路由、最终验收
  orchestrator:
    model:
      provider: "anthropic"
      model: "claude-3-5-sonnet-latest"
    toolsets: ["file", "session_search", "plan"]
    role: "Orchestrator — routes tasks and maintains team coherence"

  # 实施者：编写代码、配置、文档
  backend:
    model:
      provider: "openrouter"
      model: "anthropic/claude-3.5-sonnet"
    toolsets: ["terminal", "file", "code_execution", "web"]
    role: "Backend Builder — implements APIs, services, database"

  frontend:
    model:
      provider: "openrouter"
      model: "anthropic/claude-3.5-sonnet"
    toolsets: ["terminal", "file", "browser", "image_gen"]
    role: "Frontend Builder — builds UI components"

  reviewer:
    model:
      provider: "openrouter"
      model: "openai/gpt-4.1"
    toolsets: ["file"]
    role: "Senior reviewer — code quality and security audit"
```

### 2. 初始化团队工作区

在 Hermes 会话中：

```python
import hermes_team_orchestration as hto

team_config = {
    "orchestrator": { ... },  # 从上面的 YAML 复制
    "backend": { ... },
    "frontend": { ... },
    "reviewer": { ... }
}

hto.init_team(
    config=team_config,
    workspace="/path/to/your/project",
    shared_dir="shared",
    agents_dir="agents"
)
# 输出: {"status": "initialized", "workspace": "...", "agents": [...]}
```

这会在项目目录创建：
- `.hermes-team/config.yaml`（您的配置）
- `.hermes-team/tasks.jsonl`（任务注册表）
- `agents/orchestrator/SOUL.md` 等（自动生成）
- `shared/` 目录（交付物存放处）

### 3. 处理一个复杂请求

```python
# 接收用户需求
request = "实现用户注册、登录、JWT 刷新流程，前后端分离"

# 1️⃣ 规划
plan = hto.plan_request(
    request=request,
    agent="orchestrator",
    use_planning_skill=True  # 如果未加载 writing-plans，则用启发式拆分
)

# 2. 从规划生成任务
tasks = []
for item in plan["plan_tasks"]:
    task = hto.create_task(
        title=item["title"],
        description=item["description"],
        category=item.get("category", "CODE"),
        acceptance_criteria=[
            "通过单元测试覆盖率 80%",
            "代码符合项目规范",
            "包含 README 使用文档"
        ],
        artifacts=[
            "shared/backend/auth/",  # 预期产出路径
            "shared/frontend/auth/"
        ]
    )
    assignee = hto.route_task(task)  # 自动路由
    hto.assign_task(task, assignee=assignee)
    tasks.append(task)

print(f"Created {len(tasks)} tasks")

# 3. 执行（并行或串行）
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(hto.work_task, task) for task in tasks]
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        print(f"Task {result['task_id']} → {result['status']}")

# 4. 评审
tasks_to_review = hto.list_tasks(status="REVIEW")
for task in tasks_to_review:
    print(f"Reviewing {task['task_id']}...")
    review = hto.review_task(task, reviewer="reviewer")
    if review["approved"]:
        hto.complete_task(task)
        print("  ✓ Completed")
    else:
        print(f"  ✗ Needs work: {review['feedback'][:200]}")
        hto.assign_task(task, assignee="backend")  # 退回去修改

# 5. 完成
done_count = len(hto.list_tasks(status="DONE"))
print(f"\n✅ All done! {done_count}/{len(tasks)} tasks completed.")
```

## 自定义路由

创建 `.hermes-team/routing.json`：

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
      "subcategory": "javascript",
      "preferred_agent": "frontend"
    },
    {
      "category": "DOCS",
      "preferred_agent": "orchestrator"
    },
    {
      "category": "PLAN",
      "preferred_agent": "orchestrator"
    }
  ],
  "fallback": {"default_agent": "orchestrator"}
}
```

## 钩子回调

```python
# 任务状态变化时自动触发
def on_task_reviewed(task):
    print(f"Task {task['task_id']} entered REVIEW stage")
    # 发送到 Slack/飞书
    send_notification(f"Review needed: {task['title']}")

hto.on_transition("IN_PROGRESS", "REVIEW", on_task_reviewed)
```

## 查询和监控

```python
# 列出所有任务
all_tasks = hto.list_tasks()

# 按状态过滤
in_progress = hto.list_tasks(status="IN_PROGRESS")
builder_load = hto.list_tasks(assignee="backend", status="IN_PROGRESS")

# 代理状态
print(hto.get_agent_status("backend"))
# {
#   "agent": "backend",
#   "role": "...",
#   "active_tasks": 2,
#   "tasks": [...]
# }

# 查询共享 artifacts
artifacts = hto.query_artifacts(type="code", contains="auth")
```

## 与现有技能集成

- **writing-plans**: `plan_request()` 调用它生成详细规划
- **test-driven-development**: 配置 builder 遵循 TDD 规范
- **requesting-code-review**: 内置 review 流程类似但更轻量

## 故障排除

### 工具未出现
```bash
# 检查工具目录
ls ~/.hermes/hermes-agent/tools/
# 应该有 hermes_team_orchestration.py 或软链接

# 重新发现工具
# 在 Hermes 中执行：discover_builtin_tools()

# 查看技能是否加载
skill_info = skill_view("hermes-team-orchestration")
```

### 代理模型错误
```python
cfg = hto.load_config()
print(json.dumps(cfg, indent=2))
# 检查模型提供商和名称是否正确
```

### 任务不前进
```python
task = hto.get_task("task_id")
print(task["history"])
# 查看状态转换历史

# 强制失败
hto.fail_task(task, reason="Subagent timeout after 300s")
```

### 网络限制（OpenRouter）

如果您的环境无法访问 `openrouter.ai`，将提供者改为 Hermes 本地模型：

```yaml
builder:
  model:
    provider: "hermes"
    model: "local-llama3-8b"  # 或可用的本地模型
```

## 完整项目结构示例

```
ecommerce-api/
├── src/
│   ├── backend/           # 后端代码（由 builder 生成）
│   └── frontend/          # 前端代码
├── docs/                  # 文档
├── tests/
├── .hermes-team/
│   ├── config.yaml       # 团队配置
│   ├── tasks.jsonl       # 任务列表
│   ├── routing.json      # 路由规则
│   ├── task_01ab34cd/    # 任务目录
│   │   ├── spec.md
│   │   ├── artifacts/    # → shared/backend/auth/
│   │   ├── handoff.md
│   │   └── review.json
│   └── agents/
│       ├── orchestrator/SOUL.md
│       ├── backend/SOUL.md
│       └── reviewer/SOUL.md
├── shared/                # 所有交付物最终归档
│   ├── backend/auth/
│   ├── frontend/auth/
│   ├── docs/api-spec.md
│   └── manifest.json
└── README.md
```

## 迁移自 OpenClaw agent-swarm

1. 提取 `agent-swarm/config.json` 中的 agents 和 model 配置
2. 转换为 YAML 格式
3. 编写 routing.json（原 `router.py` 逻辑）
4. 在 Hermes 中调用 `hto.work_task()` 替代 `sessions_spawn()`

---

完成！现在您的 Hermes 代理团队已就绪，可以编排复杂任务了 🚀