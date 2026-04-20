from .hermes_team_orchestration import (
    init_team, create_task, assign_task, work_task,
    review_task, complete_task, fail_task, route_task,
    list_tasks, get_task, get_agent_status,
    plan_request, on_transition, register_artifact, query_artifacts,
    load_config, save_config
)

try:
    # Hermes registry
    from hermes import registry

    # Schema definitions
    schemas = {
        "init_team": {
            "name": "hto_init_team",
            "description": "Initialize a team orchestration workspace with agent roles and configuration",
            "parameters": {
                "type": "object",
                "properties": {
                    "config": {
                        "type": "object",
                        "description": "Team configuration mapping agent names to model, toolsets, and role"
                    },
                    "workspace": {
                        "type": "string",
                        "description": "Root workspace path"
                    },
                    "shared_dir": {
                        "type": "string",
                        "description": "Shared artifacts directory name (default: 'shared')",
                        "default": "shared"
                    },
                    "agents_dir": {
                        "type": "string",
                        "description": "Agent workspaces directory name (default: 'agents')",
                        "default": "agents"
                    }
                },
                "required": ["config", "workspace"]
            }
        },
        "create_task": {
            "name": "hto_create_task",
            "description": "Create a new task in the team registry",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"},
                    "category": {"type": "string", "description": "Category: CODE, DOCS, RESEARCH, DESIGN, GENERAL", "default": "GENERAL"},
                    "priority": {"type": "integer", "description": "Priority: 1=high, 2=medium, 3=low", "default": 1},
                    "assignee": {"type": "string", "description": "Agent name to assign (None for unassigned)"},
                    "artifacts": {"type": "array", "items": {"type": "string"}, "description": "Expected output artifact paths"},
                    "acceptance_criteria": {"type": "array", "items": {"type": "string"}, "description": "List of acceptance criteria"}
                },
                "required": ["title", "description"]
            }
        },
        "assign_task": {
            "name": "hto_assign_task",
            "description": "Assign a task to an agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "object", "description": "Task dict from create_task"},
                    "assignee": {"type": "string", "description": "Agent name"}
                },
                "required": ["task", "assignee"]
            }
        },
        "work_task": {
            "name": "hto_work_task",
            "description": "Execute a task via delegate_task (builds prompt with agent role and task spec)",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "object", "description": "Task dict from create_task"},
                    "agent": {"type": "string", "description": "Agent to execute (defaults to task.assignee or auto-route)"}
                },
                "required": ["task"]
            }
        },
        "review_task": {
            "name": "hto_review_task",
            "description": "Review a completed task; auto-approve or return for rework",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "object", "description": "Task in REVIEW status"},
                    "reviewer": {"type": "string", "description": "Reviewer agent name (default auto-route)"},
                    "approval_threshold": {"type": "number", "description": "Min score to approve (0-1)", "default": 0.8}
                },
                "required": ["task"]
            }
        },
        "complete_task": {
            "name": "hto_complete_task",
            "description": "Mark task DONE and archive artifacts",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "object", "description": "Task dict in DONE status"}
                },
                "required": ["task"]
            }
        },
        "fail_task": {
            "name": "hto_fail_task",
            "description": "Mark task FAILED with reason",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "object", "description": "Task dict"},
                    "reason": {"type": "string", "description": "Failure explanation"}
                },
                "required": ["task", "reason"]
            }
        },
        "route_task": {
            "name": "hto_route_task",
            "description": "Smart routing: select best agent based on category and config",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "object", "description": "Task dict"},
                    "available_agents": {"type": "array", "items": {"type": "string"}, "description": "Optional agent list"}
                },
                "required": ["task"]
            }
        },
        "list_tasks": {
            "name": "hto_list_tasks",
            "description": "List tasks, optionally filtered by status or assignee",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status"},
                    "assignee": {"type": "string", "description": "Filter by agent"}
                }
            }
        },
        "get_task": {
            "name": "hto_get_task",
            "description": "Get single task by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task identifier"}
                },
                "required": ["task_id"]
            }
        },
        "get_agent_status": {
            "name": "hto_get_agent_status",
            "description": "Get agent configuration and active tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent": {"type": "string", "description": "Agent name"}
                },
                "required": ["agent"]
            }
        },
        "plan_request": {
            "name": "hto_plan_request",
            "description": "Use orchestrator to break a complex request into structured tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {"type": "string", "description": "User request or project goal"},
                    "agent": {"type": "string", "description": "Agent to do planning (default: orchestrator)"},
                    "use_planning_skill": {"type": "boolean", "description": "Use writing-plans skill if available", "default": True}
                },
                "required": ["request"]
            }
        },
        "on_transition": {
            "name": "hto_on_transition",
            "description": "Register a callback for status transitions (e.g., to send notifications)",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_status": {"type": "string", "description": "Pre-transition status"},
                    "to_status": {"type": "string", "description": "Post-transition status"},
                    "callback_name": {"type": "string", "description": "Name of callback function (for tracking)"}
                },
                "required": ["from_status", "to_status", "callback_name"]
            }
        },
        "register_artifact": {
            "name": "hto_register_artifact",
            "description": "Register an artifact in the central registry",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID that produced artifact"},
                    "path": {"type": "string", "description": "File path (relative or absolute)"},
                    "type": {"type": "string", "description": "Artifact type (code, doc, data, etc.)"},
                    "description": {"type": "string", "description": "Description"}
                },
                "required": ["task_id", "path", "type", "description"]
            }
        },
        "query_artifacts": {
            "name": "hto_query_artifacts",
            "description": "Query registered artifacts by type or content",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "description": "Filter by artifact type"},
                    "contains": {"type": "string", "description": "Filter by description/path substring"}
                }
            }
        }
    }

    # Register each tool
    def _check() -> bool:
        """Check dependencies (none beyond core Hermes)"""
        return True

    def _handler(name: str, args: dict, **kw):
        """Dispatch to the correct function"""
        func = {
            "init_team": init_team,
            "create_task": create_task,
            "assign_task": assign_task,
            "work_task": work_task,
            "review_task": review_task,
            "complete_task": complete_task,
            "fail_task": fail_task,
            "route_task": route_task,
            "list_tasks": list_tasks,
            "get_task": get_task,
            "get_agent_status": get_agent_status,
            "plan_request": plan_request,
            "on_transition": on_transition,
            "register_artifact": register_artifact,
            "query_artifacts": query_artifacts
        }[name]
        return func(**args)

    # Register all tools
    for tool_name, schema in schemas.items():
        registry.register(
            name=schema["name"],
            toolset="hermes-team",
            schema=schema,
            handler=lambda a=tool_name, **kw: _handler(a, kw),
            check_fn=_check,
            emoji="🤝",
            max_result_size_chars=16000
        )

    print("🔗 hermes-team-orchestration tools registered")
except ImportError:
    # Not running inside Hermes
    pass