#!/usr/bin/env python3
"""
最小示例：3步初始化一个 2 人团队并执行任务
"""

import hermes_team_orchestration as hto

# 1. 定义团队（最简单的版本）
team = {
    "orchestrator": {
        "model": {"provider": "anthropic", "model": "claude-3-5-sonnet-latest"},
        "toolsets": ["file"],
        "role": "Router and approver"
    },
    "builder": {
        "model": {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
        "toolsets": ["file", "terminal", "code_execution"],
        "role": "Implementer"
    }
}

# 2. 初始化团队工作区
workspace = "/tmp/my-team-demo"  # 改成你的项目目录
hto.init_team(team, workspace=workspace)
print("✅ 团队初始化完成")

# 3. 创建一个简单任务
task = hto.create_task(
    title="分析高考录取数据",
    description="读取 CSV 文件，统计 2025 年北航/北理工/人大/北邮在各专业的录取分数分布",
    category="RESEARCH",
    acceptance_criteria=["输出 CSV 汇总表", "标注各专业平均分"]
)

# 4. 自动路由并执行
assignee = hto.route_task(task)  # 会根据 category 自动选择 builder
hto.assign_task(task, assignee=assignee)

print(f"🚀 任务路由到: {assignee}")
result = hto.work_task(task)
print(f"📊 执行结果: {result['status']}")

# 5. 评审（如果实现正确会自动进入 REVIEW）
if result['status'] == 'REVIEW':
    review = hto.review_task(task, reviewer="orchestrator")
    if review['approved']:
        hto.complete_task(task)
        print("✅ 任务完成")
    else:
        print(f"❌ 需要修改: {review['feedback'][:100]}")