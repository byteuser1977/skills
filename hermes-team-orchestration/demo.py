#!/usr/bin/env python3
"""
Hermes Team Orchestration — Quick Start Demo

This script demonstrates the full workflow: init, plan, route, build, review, complete.

Run inside Hermes Agent session after loading the skill.
"""

import hermes_team_orchestration as hto
import json
from pathlib import Path

# -----------------------------------------
# CONFIGURATION
# -----------------------------------------
workspace = Path("/tmp/demo-hermes-team").resolve()
workspace.mkdir(exist_ok=True)

team_config = {
    "orchestrator": {
        "model": {"provider": "anthropic", "model": "claude-3-5-sonnet-latest"},
        "toolsets": ["file", "session_search"],
        "role": "Orchestrator — plans, routes, final approval"
    },
    "builder": {
        "model": {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
        "toolsets": ["terminal", "file", "code_execution"],
        "role": "Builder — implements features"
    },
    "reviewer": {
        "model": {"provider": "openrouter", "model": "openai/gpt-4.1"},
        "toolsets": ["file"],
        "role": "Reviewer — quality gate"
    }
}

# -----------------------------------------
# 1. INITIALIZE TEAM
# -----------------------------------------
print("==> Initializing team...")
result = hto.init_team(team_config, workspace=str(workspace))
print(json.dumps(result, indent=2))

# -----------------------------------------
# 2. PLAN REQUEST
# -----------------------------------------
user_request = "Create a Python CLI todo list app with add/remove/list commands"

print(f"\n==> Planning request: '{user_request}'")
plan = hto.plan_request(user_request, agent="orchestrator", use_planning_skill=False)
print("Plan overview:", plan.get("plan"))
print("Tasks breakdown:")
for i, task_item in enumerate(plan["plan_tasks"], 1):
    print(f"  {i}. {task_item['title']} [{task_item.get('category', 'GENERAL')}]")

# Create tasks from plan tasks
tasks = []
for task_item in plan["plan_tasks"]:
    task = hto.create_task(
        title=task_item["title"],
        description=task_item["description"],
        category=task_item.get("category", "CODE"),
        acceptance_criteria=[
            "Code runs without errors",
            "All files in shared/todo-app/",
            "README with usage instructions"
        ]
    )
    assignee = hto.route_task(task)
    hto.assign_task(task, assignee=assignee)
    tasks.append(task)
    print(f"Created & assigned task {task['task_id']} to {assignee}")

# -----------------------------------------
# 3. EXECUTE TASKS (CONCURRENT)
# -----------------------------------------
print("\n==> Executing tasks...")

# Sequential demo (easier to follow)
results = []
for task in tasks:
    print(f"\nWorking on task {task['task_id']}: {task['title']}")
    result = hto.work_task(task)
    results.append(result)
    print(f"  → Status: {result['status']}")
    # Show handoff preview
    handoff = result.get('handoff', '')[:200]
    print(f"  → Handoff: {handoff}...")

# -----------------------------------------
# 4. REVIEW
# -----------------------------------------
print("\n==> Reviewing tasks in REVIEW stage...")
tasks_needing_review = hto.list_tasks(status="REVIEW")
print(f"Found {len(tasks_needing_review)} tasks to review")

for task in tasks_needing_review:
    print(f"\nReviewing task {task['task_id']}: {task['title']}")
    review = hto.review_task(task, reviewer="reviewer")
    print(f"  Approved: {review['approved']}")
    print(f"  Score: {review.get('score', 0)}")
    print(f"  Feedback: {review.get('feedback', '')[:200]}")
    if review['approved']:
        hto.complete_task(task)
        print(f"  ✓ Task completed")
    else:
        print(f"  ✗ Task needs rework — reassigning to builder")
        hto.assign_task(task, assignee="builder")
        # Could loop and re-work here

# -----------------------------------------
# 5. FINAL STATUS
# -----------------------------------------
print("\n==> Final task status")
all_tasks = hto.list_tasks()
for t in all_tasks:
    print(f"  [{t['status']}] {t['task_id']}: {t['title']} (assignee={t.get('assignee')})")

# Show shared artifacts
shared_dir = workspace / "shared"
if shared_dir.exists():
    print("\nShared artifacts:")
    for root, dirs, files in os.walk(str(shared_dir)):
        level = root.replace(str(shared_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 2 * (level + 1)
        for f in files:
            print(f"{sub_indent}{f}")

print("\n✅ Demo complete!")