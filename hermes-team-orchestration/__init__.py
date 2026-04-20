#!/usr/bin/env python3
"""
Hermes Team Orchestration — Full Skill Package

Install:
  1. Copy this directory to ~/.hermes/skills/hermes-team-orchestration/
  2. Or symlink tools/hermes_team_orchestration_register.py to ~/.hermes/hermes-agent/tools/

Usage:
  import hermes_team_orchestration as hto
  hto.init_team(config, workspace="/path/to/project")
  # Then orchestrate tasks...
"""

# Export public API
from hermes_team_orchestration import (
    init_team, create_task, assign_task, work_task,
    review_task, complete_task, fail_task, route_task,
    list_tasks, get_task, get_agent_status,
    plan_request, on_transition, register_artifact, query_artifacts,
    load_config, save_config
)

__all__ = [
    "init_team", "create_task", "assign_task", "work_task",
    "review_task", "complete_task", "fail_task", "route_task",
    "list_tasks", "get_task", "get_agent_status",
    "plan_request", "on_transition", "register_artifact", "query_artifacts",
    "load_config", "save_config"
]