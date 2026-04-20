---
name: hermes-team-orchestration
displayName: Hermes Team Orchestration
description: Multi-agent team orchestration for Hermes — route tasks to specialized agents, manage task lifecycle (planning → building → reviewing), and coordinate complex workflows with role-based agents.
version: 1.0.0
author: Hermes Agent + Your Team
license: MIT
metadata:
  hermes:
    tags: [orchestration, multi-agent, team, routing, workflow, planning, delegation]
    homepage: https://github.com/your-org/hermes-team-orchestration
    related_skills: [subagent-driven-development, writing-plans, requesting-code-review, hermes-agent]
---

# Hermes Team Orchestration

Production playbook for running multi-agent teams within Hermes with role-based routing, task lifecycle management, and quality gates.

## What This Skill Does

This skill provides a complete framework for:
1. **Task Planning** — Breaking complex requests into structured tasks
2. **Smart Routing** — Assigning tasks to the right agent/model based on role and capabilities
3. **Lifecycle Management** — Tracking tasks through stages: Plan → Build → Review → Done
4. **Quality Gates** — Mandatory reviews before task completion
5. **Artifact Management** — Shared workspace for team outputs

Unlike OpenClaw's `agent-swarm`, this uses Hermes-native `delegate_task` and works with any Hermes provider.

---

## Quick Start

### Minimal 2-Agent Team

```python
from hermes_tools import hermes_team_orchestration as hto

# 1. Define team configuration
team_config = {
    "orchestrator": {
        "model": {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
        "role": "Route tasks, track state, make priority calls"
    },
    "builder": {
        "model": {"provider": "openrouter", "model": "anthropic/claude-3.5-haiku"},
        "role": "Implement features, produce artifacts"
    }
}

# 2. Initialize team
hto.init_team(team_config, workspace="/path/to/workspace")

# 3. Create and route a task
task = hto.create_task(
    title="Implement user authentication",
    description="Add JWT-based login with refresh tokens",
    category="CODE"
)
hto.assign_task(task, assignee="builder")
hto.work_task(task)  # Blocks until Review stage
hto.review_task(task, reviewer="orchestrator")
hto.complete_task(task)
```

### 3-Agent Team with Reviewer

```python
team_config = {
    "orchestrator": {
        "model": {"provider": "anthropic", "model": "claude-3-5-sonnet-latest"},
        "role": "Orchestrator — routes, prioritizes, reports"
    },
    "builder": {
        "model": {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
        "toolsets": ["terminal", "file", "code_execution"],
        "role": "Builder — executes work, produces artifacts"
    },
    "reviewer": {
        "model": {"provider": "openrouter", "model": "openai/gpt-4.1"},
        "toolsets": ["file"],
        "role": "Reviewer — verifies quality, catches gaps"
    }
}

hto.init_team(team_config, workspace="/projects/myapp")
```

---

## Core Concepts

### Roles

| Role | Purpose | Model Guidance | Typical Toolsets |
|------|---------|---------------|------------------|
| **Orchestrator** | Route tasks, track state, make priority calls | High-reasoning (Claude, GPT-4.5) | file, session_search |
| **Builder** | Produce artifacts — code, docs, configs | Mid-to-top tier (Sonnet, Gemini) | terminal, file, code_execution, browser |
| **Reviewer** | Verify quality, push back on gaps | High-reasoning (same as orchestrator) | file |
| **Ops** | Cron jobs, health checks, dispatching | Cheapest reliable (Haiku, MiniMax) | terminal |

**Rule**: One agent, one primary role. Overlap causes confusion.

### Task States

```
PLANNING → ASSIGNED → IN_PROGRESS → REVIEW → DONE
                                    ↓
                                  FAILED (with reason)
```

**Rules**:
- Orchestrator owns state transitions (don't let agents self-assign status)
- Every transition gets a comment (who, what, why)
- `FAILED` is a valid end state — capture why and move on

### Handoffs

When work passes between agents, the handoff message must include:

1. **What was done** — summary of changes/output
2. **Where artifacts are** — exact file paths
3. **How to verify** — test commands or acceptance criteria
4. **Known issues** — anything incomplete or risky
5. **What's next** — clear next action

**Bad handoff**: "Done, check the files."
**Good handoff**: "Built auth module at `/shared/artifacts/auth/`. Run `npm test auth` to verify. Known issue: rate limiting not implemented. Next: reviewer checks error handling."

---

## API Reference

### Initialization

```python
hto.init_team(
    config: dict,                    # Team configuration (see below)
    workspace: str,                  # Root workspace path
    shared_dir: str = "shared",     # Shared artifacts directory name
    agents_dir: str = "agents"      # Agent workspaces directory name
)
```

**Team Config Structure**:

```python
{
    "orchestrator": {
        "model": {"provider": "anthropic", "model": "claude-3-5-sonnet-latest"},
        "toolsets": ["file", "session_search"],
        "role": "Orchestrator — routes, prioritizes, reports"
    },
    "builder": {
        "model": {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
        "toolsets": ["terminal", "file", "code_execution"],
        "role": "Builder — implements features"
    },
    "reviewer": {
        "model": {"provider": "openrouter", "model": "openai/gpt-4.1"},
        "toolsets": ["file"],
        "role": "Reviewer — verifies quality"
    }
}
```

### Task Creation

```python
task = hto.create_task(
    title: str,
    description: str,
    category: str = "GENERAL",      # CODE, DOCS, RESEARCH, DESIGN, etc.
    priority: int = 1,              # 1=high, 2=medium, 3=low
    assignee: str = None,          # Agent name or None for unassigned
    artifacts: list = None,        # Expected output paths
    acceptance_criteria: list = None
) -> dict
```

Returns a task dictionary with `task_id`, `status`, `created_at`, etc.

### Task Assignment

```python
hto.assign_task(task: dict, assignee: str) -> dict
```

Updates task with `assignee` and changes status to `ASSIGNED`. Adds assignment comment.

### Task Execution

```python
result = hto.work_task(task: dict, agent: str = None) -> dict
```

**What it does**:
1. Spawns a subagent via `delegate_task` with task details
2. Subagent executes and produces artifacts
3. Updates task status to `IN_PROGRESS` → `REVIEW`
4. Returns subagent result

**Parameters**:
- `task`: task dictionary from `create_task`
- `agent`: which agent to use (defaults to task's assignee or orchestrator if None)

**Agent context injected automatically**:
- Team role definition
- Task specification
- Workspace paths
- Handoff instructions
- Previous task history (if any)

### Task Review

```python
passed = hto.review_task(
    task: dict,
    reviewer: str = None,
    approval_threshold: float = 0.8
) -> dict
```

**What it does**:
1. Spawns reviewer subagent
2. Reviewer checks artifacts against acceptance criteria
3. Returns review result: `{"approved": bool, "feedback": str, "score": float}`

**If not approved**: task stays in `REVIEW` status; builder must fix and resubmit.

### Task Completion

```python
hto.complete_task(task: dict) -> dict
```

Marks task as `DONE`, archives artifacts to shared directory, updates team index.

### Task Failure

```python
hto.fail_task(task: dict, reason: str) -> dict
```

Marks task as `FAILED` with failure reason. Must provide clear explanation.

### Routing

```python
agent = hto.route_task(task: dict, available_agents: list = None) -> str
```

Smart routing based on:
- Task category (CODE, DOCS, RESEARCH, etc.)
- Required toolsets (inferred from description)
- Agent capabilities and current load

**Custom routing rules** (edit `config/routing.json`):

```json
{
  "CODE": {
    "preferred_agent": "builder",
    "required_tools": ["terminal", "file", "code_execution"],
    "fallback_agent": "orchestrator"
  },
  "DOCS": {
    "preferred_agent": "builder",
    "required_tools": ["file"]
  }
}
```

### Status Queries

```python
# List all tasks in workspace
tasks = hto.list_tasks(status: str = None) -> list

# Get task details
task = hto.get_task(task_id: str) -> dict

# Get agent status
status = hto.get_agent_status(agent: str) -> dict
```

---

## Workspace Layout

```
/workspace/
├── .hermes-team/                 # Team orchestration metadata
│   ├── config.yaml              # Team configuration
│   ├── tasks.jsonl              # Task registry (append-only)
│   ├── task_N/                  # Individual task directory
│   │   ├── spec.md              # Task specification
│   │   ├── artifacts/           # Output files
│   │   ├── review.json          # Review results
│   │   └── handoff.md           # Handoff notes
│   └── agents/
│       ├── orchestrator/
│       │   └── SOUL.md          # Agent identity
│       ├── builder/
│       │   └── SOUL.md
│       └── reviewer/
│           └── SOUL.md
├── shared/                       # Shared artifacts
│   ├── specs/
│   ├── docs/
│   └── deliverables/
└── (your project files)
```

**Rules**:
- Agents read/write their own `.hermes-team/agents/<name>/` workspace freely
- All deliverables go to `shared/`
- Orhestator can read all workspaces for oversight

---

## Complete Workflow Example

```python
import hermes_team_orchestration as hto

# 1. Configure team
team = {
    "orchestrator": {
        "model": {"provider": "anthropic", "model": "claude-3-5-sonnet-latest"},
        "toolsets": ["file", "session_search", "plan"],
        "role": "Plan architecture, route tasks, final approval"
    },
    "architect": {
        "model": {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
        "toolsets": ["file", "code_execution"],
        "role": "Design system architecture, produce specs"
    },
    "backend": {
        "model": {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
        "toolsets": ["terminal", "file", "code_execution"],
        "role": "Implement backend services, APIs, database"
    },
    "frontend": {
        "model": {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
        "toolsets": ["terminal", "file", "browser"],
        "role": "Build UI components, integrate APIs"
    },
    "reviewer": {
        "model": {"provider": "openrouter", "model": "openai/gpt-4.1"},
        "toolsets": ["file"],
        "role": "Code review, security audit, quality gates"
    }
}

hto.init_team(team, workspace="/projects/ecommerce")

# 2. User request comes in
request = "Build an e-commerce API with user auth, product catalog, and checkout"

# 3. Orchestrator plans
plan = hto.plan_request(
    request,
    agent="orchestrator",
    use_planning_skill=True  # Uses writing-plans under the hood
)

# plan.plan is a markdown plan with tasks

# 4. Create tasks from plan
tasks = []
for task_item in plan.plan_tasks:  # extracted from plan
    task = hto.create_task(
        title=task_item["title"],
        description=task_item["description"],
        category=task_item.get("category", "CODE"),
        acceptance_criteria=task_item.get("acceptance", [])
    )
    # Route automatically
    assignee = hto.route_task(task)
    hto.assign_task(task, assignee=assignee)
    tasks.append(task)

# 5. Execute tasks (can be parallel)
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    futures = [pool.submit(hto.work_task, t) for t in tasks]
    results = [f.result() for f in futures]

# 6. Review all completed tasks
for task in tasks:
    if task["status"] == "REVIEW":
        review = hto.review_task(task, reviewer="reviewer")
        if review["approved"]:
            hto.complete_task(task)
        else:
            # Reassign to builder with feedback
            hto.assign_task(task, assignee="backend")  # or "frontend"
            task["description"] += f"\n\n reviewer feedback: {review['feedback']}"
            hto.work_task(task)

# 7. Final integration check
hto.run_integration_tests(agent="orchestrator")

print(" Team delivery complete!")
```

---

## Advanced Features

### Custom Routing Rules

Edit `~/.hermes/.hermes-team/routing.json`:

```json
{
  "rules": [
    {
      "category": "CODE",
      "subcategory": "python",
      "preferred_agent": "backend",
      "required_tools": ["terminal", "file", "code_execution"],
      "model_override": {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"}
    },
    {
      "category": "DOCS",
      "preferred_agent": "orchestrator",
      "required_tools": ["file"]
    }
  ],
  "fallback": {
    "default_agent": "orchestrator"
  }
}
```

### Lifecycle Hooks

Register callbacks for state transitions:

```python
hto.on_transition("PLANNING", "ASSIGNED", lambda task: print(f"Task {task['id']} assigned"))
hto.on_transition("IN_PROGRESS", "REVIEW", lambda task: hto.run_linter(task))
hto.on_transition("REVIEW", "DONE", lambda task: hto.archive_artifacts(task))
```

### Parallel Execution with Dependencies

```python
# Build dependency graph
hto.set_dependency("task-001", depends_on=[])          # First
hto.set_dependency("task-002", depends_on=["task-001"])
hto.set_dependency("task-003", depends_on=["task-001"])
hto.set_dependency("task-004", depends_on=["task-002", "task-003"])  # Wait for 2 & 3

# Execute respecting dependencies
hto.execute_plan(parallel=True, max_workers=3)
```

### Shared Artifact Registry

```python
# Register an artifact
hto.register_artifact(
    task_id="task-001",
    path="shared/api/auth.py",
    type="code",
    description="JWT authentication module"
)

# Query artifacts
auth_files = hto.query_artifacts(type="code", contains="auth")
```

---

## Integration with Existing Skills

This skill complements:

- **`writing-plans`** — Use for the initial planning phase (`use_planning_skill=True`)
- **`subagent-driven-development`** — Under the hood, each `work_task()` uses similar two-stage review
- **`test-driven-development`** — Builders can be configured to follow TDD
- **`requesting-code-review`** — The `review_task()` is a simplified inline version

---

## Best Practices

1. **Task Size**: Each task should be 2-5 minutes of focused work for a builder agent
2. **Explicit Artifacts**: Always specify expected artifact paths in `create_task(artifacts=[...])`
3. **Required Toolsets**: Match toolsets to role — don't give builders browser unless needed
4. **Model Tiers**: Orchestrator and Reviewer should use top-tier; Builders can use cost-effective models
5. **Reviews Required**: Never skip the review step — quality degrades after 3 unreviewed tasks
6. **Workspace Isolation**: Each agent should have its own SOUL.md in `agents/<name>/`
7. **Handoffs**: Always include verification steps and known issues in completion notes

---

## Migration from OpenClaw agent-swarm

| OpenClaw Feature | Hermes Equivalent |
|------------------|-------------------|
| `sessions_spawn()` | `delegate_task()` |
| `router.py` routing | `hto.route_task()` + `config.json` |
| `openclaw.json` | `config.yaml` + `.env` |
| Platform-specific MCP | Hermes native toolsets |
| `sessions_spawn` sessionTarget | `toolsets` param + workspace isolation |

**Migration steps**:
1. Extract routing rules from OpenClaw `config.json`
2. Convert to Hermes team config (model dict format)
3. Replace `sessions_spawn` calls with `hto.work_task()`
4. Use Hermes `write_file`/`read_file` instead of platform APIs

---

## Troubleshooting

### Task stuck in IN_PROGRESS

```python
# Check subagent logs
hto.get_task_logs(task_id)

# Force timeout
hto.fail_task(task_id, reason="Subagent timeout after 300s")
```

### Review loop (keep failing)

```python
# Bypass review for emergency (use sparingly)
hto.force_complete(task_id, bypass_review=True)
```

### Model errors

```python
# Check agent's model config
hto.get_agent_status("builder")["model"]

# Update model
hto.update_agent_model("builder", {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"})
```

---

## Appendix: SOUL.md Template

```
# Agent: <name>

## Role
<what this agent does>

## Scope
- Do this
- Do that
- Don't do the other thing

## Boundaries
- If unclear, ask orchestrator
- If blocked >10min, comment on task
- If architectural change needed, propose only

## Handoff Format
Every completed task must include:
1. What changed and why
2. File paths for all artifacts
3. How to test/verify
4. Known limitations
```

---

**Version**: 1.0.0
**Last Updated**: 2025-04-20
**Compatible Hermes**: >= 2.0.0
**Dependencies**: None (uses Hermes core only)