#!/usr/bin/env python3
"""
Hermes Team Orchestration — Multi-agent task router and lifecycle manager.

Adapts agent-team-orchestration concepts to Hermes architecture.
Uses delegate_task for agent spawning; manages state and handoffs.

NORMS:
- One agent, one role
- All artifacts → shared/
- Mandatory review before DONE
- Handoffs must include verification steps
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Hermes tools — importing directly works in Hermes skill context
try:
    from hermes_tools import terminal, read_file, write_file, search_files, session_search, delegate_task
except ImportError:
    # Allow skill to be read outside Hermes (e.g., documentation generation)
    terminal = read_file = write_file = search_files = session_search = delegate_task = None

__all__ = [
    "init_team", "create_task", "assign_task", "work_task",
    "review_task", "complete_task", "fail_task", "route_task",
    "list_tasks", "get_task", "get_agent_status",
    "plan_request", "on_transition", "register_artifact", "query_artifacts",
    "load_config", "save_config"
]

# Constants
TEAM_DIR = ".hermes-team"
CONFIG_FILE = "config.yaml"
TASKS_FILE = "tasks.jsonl"
SHARED_DIR = "shared"
AGENTS_DIR = "agents"

# In-memory state (would be persisted in real implementation)
_state = {
    "config": None,
    "workspace": None,
    "team_dir": None,
    "tasks": {},  # task_id -> task dict
    "callbacks": {},  # (from, to) -> list[callable]
    "artifacts": []  # artifact registry
}


def _log(msg: str):
    """Simple internal logging."""
    print(f"[hermes-team] {msg}")


def load_config() -> dict:
    """Load team configuration from workspace/.hermes-team/config.yaml."""
    if _state["config"]:
        return _state["config"]

    config_path = Path(_state["workspace"]) / TEAM_DIR / CONFIG_FILE
    if not config_path.exists():
        raise FileNotFoundError(f"Team config not found: {config_path}. Run init_team() first.")

    import yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)

    _state["config"] = config
    return config


def save_config(config: dict):
    """Save team configuration."""
    config_path = Path(_state["workspace"]) / TEAM_DIR / CONFIG_FILE
    import yaml
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    _state["config"] = config
    _log(f"Saved config to {config_path}")


def _ensure_team_dir():
    """Create team directory structure if missing."""
    workspace = Path(_state["workspace"])
    team_dir = workspace / TEAM_DIR
    team_dir.mkdir(exist_ok=True)
    (workspace / SHARED_DIR).mkdir(exist_ok=True)
    (workspace / AGENTS_DIR).mkdir(exist_ok=True)

    # Create tasks file if missing
    tasks_path = team_dir / TASKS_FILE
    if not tasks_path.exists():
        tasks_path.touch()

    _state["team_dir"] = team_dir
    _log(f"Team dir: {team_dir}")


def _append_task_to_store(task: dict):
    """Append task to tasks.jsonl."""
    tasks_path = _state["team_dir"] / TASKS_FILE
    with open(tasks_path, "a") as f:
        f.write(json.dumps(task, ensure_ascii=False) + "\n")
    _state["tasks"][task["task_id"]] = task


def _update_task_in_store(task: dict):
    """Update task in the in-memory store (tasks.jsonl is append-only)."""
    _state["tasks"][task["task_id"]] = task
    # In a full implementation, we'd also rewrite tasks.jsonl or maintain a separate index


def init_team(config: dict, workspace: str, shared_dir: str = SHARED_DIR, agents_dir: str = AGENTS_DIR):
    """
    Initialize team orchestration in a workspace.

    Args:
        config: Team configuration dict (see SKILL.md)
        workspace: Root workspace path
        shared_dir: Shared artifacts directory (relative to workspace)
        agents_dir: Agent workspaces directory (relative to workspace)
    """
    _state["workspace"] = Path(workspace).resolve()
    _ensure_team_dir()
    save_config(config)

    # Create each agent's workspace with SOUL.md
    for agent_name in config:
        agent_dir = _state["workspace"] / agents_dir / agent_name
        agent_dir.mkdir(exist_ok=True)
        soul_path = agent_dir / "SOUL.md"
        if not soul_path.exists():
            role = config[agent_name].get("role", "Agent")
            toolsets = ", ".join(config[agent_name].get("toolsets", []))
            soul_content = f"""# Agent: {agent_name}

## Role
{role}

## Scope
- Execute tasks assigned by orchestrator
- Produce artifacts in shared workspace
- Report status updates

## Boundaries
- Don't reassign tasks
- Don't mark own tasks DONE (orchestrator does that)
- If blocked >10min, add task comment and await instructions

## Handoff Format
When completing work:
1. Summary: What changed and why
2. Artifacts: Exact file paths in {shared_dir}/
3. Verification: Test commands or manual checks
4. Known issues: Incomplete items or risks
5. Next: What should happen next

## Tools
{toolsets or "None specified"}
"""
            write_file(path=str(soul_path), content=soul_content)
            _log(f"Created SOUL.md for {agent_name}")

    _log(f"Team initialized in workspace: {workspace}")
    _log(f"Agents: {', '.join(config.keys())}")
    return {"status": "initialized", "workspace": workspace, "agents": list(config.keys())}


def create_task(
    title: str,
    description: str,
    category: str = "GENERAL",
    priority: int = 1,
    assignee: Optional[str] = None,
    artifacts: Optional[List[str]] = None,
    acceptance_criteria: Optional[List[str]] = None
) -> dict:
    """
    Create a new task in the team task registry.

    Returns task dict with task_id.
    """
    task_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat() + "Z"

    task = {
        "task_id": task_id,
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
        "status": "PLANNING",
        "assignee": assignee,
        "artifacts": artifacts or [],
        "acceptance_criteria": acceptance_criteria or [],
        "created_at": now,
        "updated_at": now,
        "history": [
            {"timestamp": now, "event": "created", "by": "user", "details": None}
        ]
    }

    _append_task_to_store(task)
    _log(f"Created task {task_id}: {title[:50]}")
    return task


def _transition_task(task: dict, new_status: str, by: str, details: Optional[str] = None):
    """Internal: transition task status with audit trail."""
    old_status = task["status"]
    task["status"] = new_status
    task["updated_at"] = datetime.utcnow().isoformat() + "Z"

    # Record transition
    task["history"].append({
        "timestamp": task["updated_at"],
        "event": "transition",
        "by": by,
        "details": {"from": old_status, "to": new_status, "notes": details}
    })

    _update_task_in_store(task)

    # Trigger callbacks
    key = (old_status, new_status)
    if key in _state["callbacks"]:
        for cb in _state["callbacks"][key]:
            try:
                cb(task)
            except Exception as e:
                _log(f"Callback error: {e}")

    _log(f"Task {task['task_id']}: {old_status} → {new_status} (by {by})")


def assign_task(task: dict, assignee: str) -> dict:
    """
    Assign task to an agent.

    Changes status from PLANNING/UNASSIGNED to ASSIGNED.
    """
    valid_agents = load_config().keys()
    if assignee not in valid_agents:
        raise ValueError(f"Unknown agent '{assignee}'. Valid agents: {', '.join(valid_agents)}")

    if task["status"] not in ["PLANNING", "UNASSIGNED"]:
        _log(f"Warning: assigning task in status {task['status']}")

    task["assignee"] = assignee
    _transition_task(task, "ASSIGNED", by="orchestrator", details=f"Assigned to {assignee}")
    return task


def route_task(task: dict, available_agents: Optional[List[str]] = None) -> str:
    """
    Smart routing: select the best agent for a task.

    Rules:
    1. Respect existing assignee if set
    2. Match task category to agent capabilities (from routing.json if exists)
    3. Default to orchestrator
    """
    # Already assigned?
    if task["assignee"]:
        _log(f"Task {task['task_id']} already assigned to {task['assignee']}")
        return task["assignee"]

    available_agents = available_agents or list(load_config().keys())

    # Load custom routing rules if present
    routing_path = _state["team_dir"] / "routing.json"
    if routing_path.exists():
        with open(routing_path) as f:
            routing_rules = json.load(f)
    else:
        routing_rules = {"fallback": {"default_agent": "orchestrator"}}

    category = task.get("category", "GENERAL").upper()

    # Try to match rule
    for rule in routing_rules.get("rules", []):
        if rule.get("category") == category:
            preferred = rule.get("preferred_agent")
            if preferred in available_agents:
                _log(f"Routed task {task['task_id']} to {preferred} (by category {category})")
                return preferred

    # Fallback
    default = routing_rules.get("fallback", {}).get("default_agent", "orchestrator")
    if default in available_agents:
        _log(f"Routed task {task['task_id']} to {default} (fallback)")
        return default
    else:
        raise ValueError(f"No suitable agent found. Available: {available_agents}")


def work_task(task: dict, agent: Optional[str] = None) -> dict:
    """
    Execute a task via delegate_task.

    Loads agent SOUL.md for context, injects task spec, and runs.
    On completion, status → REVIEW.
    """
    assignee = agent or task.get("assignee")
    if not assignee:
        # Auto-route
        assignee = route_task(task)

    config = load_config()
    if assignee not in config:
        raise ValueError(f"Agent {assignee} not in config")

    agent_cfg = config[assignee]

    # Build prompt
    agent_dir = _state["workspace"] / AGENTS_DIR / assignee
    soul_path = agent_dir / "SOUL.md"
    soul_content = ""
    if soul_path.exists():
        soul_content = read_file(path=str(soul_path))["content"]

    # Build handoff spec
    spec = f"""# Task Execution: {task['title']}

## Agent Role
{agent_cfg.get('role', 'Execute tasks')}

## Task Specification
- ID: {task['task_id']}
- Title: {task['title']}
- Description: {task['description']}
- Category: {task.get('category')}
- Priority: {task.get('priority')}

## Acceptance Criteria
{chr(10).join(f'- {c}' for c in task.get('acceptance_criteria', ['None specified']))}

## Workspace
- Team dir: {_state['team_dir']}
- Shared artifacts dir: {SHARED_DIR}/
- Your private dir: agents/{assignee}/

## Instructions
1. Create a working directory under your agent space if needed
2. Implement/design/research as described
3. Save all deliverables in the shared directory: {SHARED_DIR}/
4. When finished, produce a handoff note:
   - Summary of work done
   - List of artifacts (full paths)
   - How to verify
   - Known issues
   - Next action (if any)
5. Return the handoff as your final message.

## Handoff Format
```
**Work Summary:**
[What was done]

**Artifacts:**
- path/to/file1 (description)
- path/to/file2

**Verification:**
[How to test/check]

**Known Issues:**
[Limitations, incomplete items]

**Next:**
[What should happen next]
```
"""

    # Inject agent's own SOUL for self-reference
    full_prompt = f"{soul_content}\n\n---\n\nTeam Instructions:\n{spec}"

    _log(f"Dispatching task {task['task_id']} to {assignee}")
    _transition_task(task, "IN_PROGRESS", by="orchestrator", details=f"Assigned to {assignee}")

    # Call delegate_task (Hermes tool)
    try:
        result = delegate_task(
            goal=full_prompt,
            context="",
            model=agent_cfg["model"],
            toolsets=agent_cfg.get("toolsets", ["file"])
        )
    except Exception as e:
        _log(f"delegate_task failed: {e}")
        raise

    # Record completion (status → REVIEW)
    handoff = result.get("summary", str(result))
    task["history"].append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": "work_completed",
        "by": assignee,
        "details": {"handoff": handoff[:1000]}
    })
    _transition_task(task, "REVIEW", by="orchestrator", details="Work completed, awaiting review")

    # Store handoff artifact
    handoff_path = _state["team_dir"] / f"task_{task['task_id']}_handoff.md"
    write_file(path=str(handoff_path), content=handoff)
    task["artifacts"].append(str(handoff_path))

    _log(f"Task {task['task_id']} entered REVIEW stage")
    return {"task_id": task["task_id"], "status": "REVIEW", "handoff": handoff, "result": result}


def review_task(task: dict, reviewer: str = None, approval_threshold: float = 0.8) -> dict:
    """
    Review task completion.

    Spawns reviewer agent to verify artifacts meet acceptance criteria.
    Returns: {"approved": bool, "feedback": str, "score": float}
    """
    if task["status"] != "REVIEW":
        raise ValueError(f"Task {task['task_id']} is {task['status']}, not REVIEW")

    reviewer = reviewer or route_task(task, available_agents=list(load_config().keys()))
    if reviewer not in load_config():
        raise ValueError(f"Reviewer {reviewer} not in config")

    config = load_config()
    agent_cfg = config[reviewer]

    # Build review prompt
    spec = task
    handoff_path = _state["team_dir"] / f"task_{task['task_id']}_handoff.md"
    handoff_content = ""
    if handoff_path.exists():
        handoff_content = read_file(path=str(handoff_path))["content"]

    review_prompt = f"""# Task Review

## Task
- Title: {spec['title']}
- Description: {spec['description']}
- Acceptance Criteria:
{chr(10).join(f'  - {c}' for c in spec.get('acceptance_criteria', ['None']))}

## Submission (Builder's Handoff)
```
{handoff_content}
```

## Instructions
Evaluate the submission against the acceptance criteria.

**Checklist:**
1. All listed artifacts present?
2. Artifacts match specification?
3. Verification steps provided and executable?
4. Known issues disclosed?
5. Quality: Is this production-ready?

**Output format (JSON):**
```json
{{
  "approved": true/false,
  "score": 0.95,  // float 0-1
  "feedback": "Detailed reasoning...",
  "missing_criteria": ["list any unmet criteria"],
  "suggestions": ["improvements"]
}}
```

Return ONLY valid JSON. No markdown wrappers.
"""

    _log(f"Starting review for task {task['task_id']} by {reviewer}")

    try:
        result = delegate_task(
            goal=review_prompt,
            context="",
            model=agent_cfg["model"],
            toolsets=agent_cfg.get("toolsets", ["file"])
        )
    except Exception as e:
        _log(f"Review delegate failed: {e}")
        raise

    # Parse JSON response from agent
    try:
        # Assume agent returns JSON in output
        output = result.get("summary", str(result))
        # Extract JSON if wrapped in markdown
        import re
        json_match = re.search(r"\{.*\}", output, re.DOTALL)
        if json_match:
            review = json.loads(json_match.group())
        else:
            # Try direct parse
            review = json.loads(output)
    except json.JSONDecodeError as e:
        _log(f"Failed to parse review JSON: {e}")
        review = {"approved": False, "feedback": f"Reviewer output could not be parsed: {output[:500]}", "score": 0.0}

    # Record review
    task["history"].append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": "review",
        "by": reviewer,
        "details": {"approved": review["approved"], "score": review.get("score", 0), "feedback": review.get("feedback", "")[:500]}
    })

    if review["approved"]:
        _transition_task(task, "DONE", by="orchestrator", details=f"Review approved (score {review.get('score')})")
        _log(f"Task {task['task_id']} approved and completed")
    else:
        # Back to IN_PROGRESS for rebuild
        _transition_task(task, "IN_PROGRESS", by="orchestrator", details=f"Review failed: {review.get('feedback', 'No feedback')[:200]}")
        _log(f"Task {task['task_id']} returned to builder: {review.get('feedback', '')[:100]}")

    # Save review to file
    review_path = _state["team_dir"] / f"task_{task['task_id']}_review.json"
    write_file(path=str(review_path), content=json.dumps(review, indent=2))

    return review


def complete_task(task: dict) -> dict:
    """
    Mark task as complete (post-approval).

    - Move artifacts to shared/ if not already there
    - Update shared manifest
    """
    if task["status"] != "DONE":
        raise ValueError(f"Task {task['task_id']} is {task['status']}, not DONE")

    # Archive
    shared_dir = _state["workspace"] / SHARED_DIR
    manifest_path = shared_dir / "manifest.json"

    # Load or create manifest
    if manifest_path.exists():
        manifest = json.loads(read_file(path=str(manifest_path))["content"])
    else:
        manifest = {"artifacts": []}

    # Add task artifacts
    for art in task.get("artifacts", []):
        art_path = Path(art)
        if art_path.exists():
            rel_path = art_path.relative_to(_state["workspace"])
            manifest["artifacts"].append({
                "task_id": task["task_id"],
                "path": str(rel_path),
                "title": task["title"]
            })

    write_file(path=str(manifest_path), content=json.dumps(manifest, indent=2))
    _log(f"Task {task['task_id']} archived in shared manifest")
    return task


def fail_task(task: dict, reason: str) -> dict:
    """
    Mark task as FAILED with reason.
    """
    _transition_task(task, "FAILED", by="orchestrator", details=reason)
    _log(f"Task {task['task_id']} failed: {reason[:100]}")
    return task


def list_tasks(status: Optional[str] = None, assignee: Optional[str] = None) -> List[dict]:
    """
    List tasks from in-memory store (or reload from tasks.jsonl).
    """
    if not _state["tasks"]:
        # Load all tasks
        tasks_path = _state["team_dir"] / TASKS_FILE
        if not tasks_path.exists():
            return []
        with open(tasks_path) as f:
            for line in f:
                if line.strip():
                    task = json.loads(line)
                    _state["tasks"][task["task_id"]] = task

    tasks = list(_state["tasks"].values())

    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if assignee:
        tasks = [t for t in tasks if t.get("assignee") == assignee]

    return sorted(tasks, key=lambda t: t.get("priority", 2))


def get_task(task_id: str) -> Optional[dict]:
    """Get single task by ID."""
    return _state["tasks"].get(task_id)


def get_agent_status(agent: str) -> dict:
    """
    Get agent status: config, active tasks, etc.
    """
    config = load_config()
    if agent not in config:
        raise ValueError(f"Agent {agent} not found")

    assigned_tasks = [t for t in _state["tasks"].values() if t.get("assignee") == agent and t["status"] not in ["DONE", "FAILED"]]

    return {
        "agent": agent,
        "role": config[agent].get("role"),
        "model": config[agent].get("model"),
        "toolsets": config[agent].get("toolsets", []),
        "active_tasks": len(assigned_tasks),
        "tasks": [{"id": t["task_id"], "title": t["title"], "status": t["status"]} for t in assigned_tasks]
    }


def on_transition(from_status: str, to_status: str, callback):
    """
    Register a callback for status transitions.

    Example: on_transition("IN_PROGRESS", "REVIEW", lambda task: send_notification(task))
    """
    key = (from_status, to_status)
    if key not in _state["callbacks"]:
        _state["callbacks"][key] = []
    _state["callbacks"][key].append(callback)
    _log(f"Registered callback for {from_status}→{to_status}")


def plan_request(request: str, agent: str = "orchestrator", use_planning_skill: bool = True) -> dict:
    """
    Have orchestrator plan a complex request into tasks.

    Uses writing-plans skill if available; otherwise simple heuristic.
    """
    _log(f"Planning request with {agent}")

    agent_cfg = load_config()[agent]
    model = agent_cfg["model"]

    if use_planning_skill:
        try:
            # Use Hermes writing-plans skill if loaded
            from hermes_tools import writing_plans
            plan = writing_plans.create_plan(
                title=f"Plan: {request[:50]}",
                description=request,
                template="feature"  # or derive from keywords
            )
            # Extract tasks from plan (simplified)
            tasks = []
            for i, step in enumerate(plan.get("steps", [])):
                tasks.append({
                    "title": step.get("title", f"Step {i+1}"),
                    "description": step.get("description", ""),
                    "category": "CODE"
                })
            return {"plan": plan, "plan_tasks": tasks}
        except ImportError:
            _log("writing-plans skill not available, falling back to heuristic")

    # Simple heuristic breakdown
    prompt = f"""Break this request into 3-5 tasks, each doable in 2-5 minutes by a specialist.

Request: {request}

Output JSON with:
{{
  "plan": "Brief plan overview",
  "plan_tasks": [
    {{"title": "...", "description": "...", "category": "CODE|DOCS|RESEARCH|DESIGN"}}
  ]
}}

Return only JSON.
"""
    result = delegate_task(goal=prompt, context="", model=model, toolsets=["file"])
    output = result.get("summary", str(result))
    try:
        import re
        json_match = re.search(r"\{.*\}", output, re.DOTALL)
        if json_match:
            plan_data = json.loads(json_match.group())
            return plan_data
        else:
            # Fallback single task
            return {
                "plan": "Simple breakdown (no breakdown available)",
                "plan_tasks": [{"title": request[:50], "description": request, "category": "GENERAL"}]
            }
    except json.JSONDecodeError:
        return {
            "plan": "Failed to parse plan, using single task",
            "plan_tasks": [{"title": request[:50], "description": request, "category": "GENERAL"}]
        }


def register_artifact(task_id: str, path: str, type: str, description: str):
    """Register an artifact in the central registry."""
    art = {
        "task_id": task_id,
        "path": path,
        "type": type,
        "description": description,
        "registered_at": datetime.utcnow().isoformat() + "Z"
    }
    _state["artifacts"].append(art)
    _log(f"Registered artifact: {path}")


def query_artifacts(type: Optional[str] = None, contains: Optional[str] = None) -> List[dict]:
    """Query registered artifacts."""
    results = _state["artifacts"]
    if type:
        results = [a for a in results if a["type"] == type]
    if contains:
        results = [a for a in results if contains.lower() in a["description"].lower() or contains in a["path"]]
    return results


# =====================
# CLI / Direct Invocation
# =====================

if __name__ == "__main__":
    # Self-test mode
    import sys
    print("Hermes Team Orchestration skill module")
    print("This module is meant to be loaded by Hermes Agent.")
    print("Test import: from hermes_tools import hermes_team_orchestration as hto")
    sys.exit(0)