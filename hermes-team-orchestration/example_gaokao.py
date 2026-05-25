#!/usr/bin/env python3
"""
Hermes Team Orchestration — 高考志愿填报规划示例

针对比特大帝的真实背景：
- 一模成绩：585分
- 朝阳区排名：1350名
- 选科：物化生
- 色弱（避开化学、生物、医学相关）
- 目标：北京高校（北航、北理工、人大、北邮）
"""

import hermes_team_orchestration as hto
from pathlib import Path
import json

# ====================
# 1. 配置团队
# ====================

workspace = Path("/tmp/gaokao-team-demo").resolve()
workspace.mkdir(exist_ok=True)

team_config = {
    "orchestrator": {
        "model": {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest"
        },
        "toolsets": ["file", "session_search"],
        "role": "Orchestrator — 综合规划师，统筹志愿填报策略，最终决策"
    },
    "data_analyst": {
        "model": {
            "provider": "openrouter",
            "model": "anthropic/claude-3.5-sonnet"
        },
        "toolsets": ["file", "code_execution"],  # 可分析 CSV 数据
        "role": "Data Analyst — 分析历年录取数据，计算冲稳保概率"
    },
    "strategist": {
        "model": {
            "provider": "openrouter",
            "model": "anthropic/claude-3.5-sonnet"
        },
        "toolsets": ["file", "web"],  # 可搜索最新招生政策
        "role": "Strategist — 研究专业前景、就业趋势，优化志愿顺序"
    },
    "reviewer": {
        "model": {
            "provider": "openrouter",
            "model": "openai/gpt-4.1"
        },
        "toolsets": ["file"],
        "role": "Senior Reviewer — 审核方案安全性、完整性，确保无遗漏"
    }
}

# ====================
# 2. 初始化团队
# ====================

print("="*60)
print("高考志愿填报智能规划系统")
print("="*60)

print("\n[1] 初始化团队工作区...")
result = hto.init_team(team_config, workspace=str(workspace))
print(f"   团队状态: {result['status']}")
print(f"   工作区: {result['workspace']}")
print(f"   成员数: {len(result['agents'])} 人: {', '.join(result['agents'])}")

# ====================
# 3. 规划任务
# ====================

student_profile = {
    "name": "比特",
    "score": 585,
    "district": "朝阳区",
    "ranking": 1350,
    "subject_combination": "物理+化学+生物",
    "color_blind": True,  # 色弱，需避开化学、生物、医学相关
    "target_schools": [
        "北京航空航天大学",
        "北京理工大学",
        "中国人民大学",
        "北京邮电大学"
    ],
    "preference": "北京高校优先"
}

user_request = f"""
根据以下学生背景，制定高考志愿填报方案（冲、稳、保三层策略）：

【学生档案】
姓名：{student_profile['name']}
一模成绩：{student_profile['score']} 分
朝阳区排名：{student_profile['ranking']} 名
选科组合：{student_profile['subject_combination']}
身体状况：{'色弱（需避开化学、生物、医学类专业）' if student_profile['color_blind'] else '正常'}
志愿倾向：{student_profile['preference']}

【目标院校】
- 北京航空航天大学
- 北京理工大学
- 中国人民大学
- 北京邮电大学

【交付要求】
1. 冲（30-40分差距）：2-3 个专业组
2. 稳（10-20分差距）：3-4 个专业组
3. 保（低于或接近）：2-3 个专业组
4. 每个专业组列出 3-5 个专业，标注是否色弱限报
5. 给出志愿排序建议
6. 提供风险评估（退档风险、调剂风险）

数据文件路径：/mnt/d/workspace/openclaw-state/workspace-develop/knowledge/2026-04-17-高校录取分数线-宽表.csv
"""

print("\n[2] 创建并分解规划任务...")
plan = hto.plan_request(
    request=user_request,
    agent="orchestrator",
    use_planning_skill=False  # 使用启发式拆分
)

print(f"   规划概览：{plan.get('plan', 'N/A')}")
print(f"   分解为 {len(plan['plan_tasks'])} 个子任务")

# 创建任务
tasks = []
for idx, item in enumerate(plan["plan_tasks"]):
    task = hto.create_task(
        title=item["title"],
        description=f"{item['description']}\n\n学生档案：{json.dumps(student_profile, ensure_ascii=False, indent=2)}",
        category=item.get("category", "RESEARCH"),
        priority=idx + 1,
        acceptance_criteria=[
            "数据准确：基于 2023-2025 年录取数据",
            "色弱限制：明确标注限报专业",
            "格式规范：提供冲稳保分层建议"
        ],
        artifacts=[
            f"shared/志愿方案/任务_{idx+1}_output.md"
        ]
    )
    assignee = hto.route_task(task)  # 自动路由
    hto.assign_task(task, assignee)
    tasks.append(task)
    print(f"   ✓ 任务 {task['task_id'][:8]}: {item['title'][:40]} → 分配给 {assignee}")

# ====================
# 4. 执行任务
# ====================

print("\n[3] 开始执行任务（可并行）...")

# 串行执行，便于观察
for task in tasks:
    print(f"\n   正在执行: {task['title']}")
    print(f"   状态: {task['status']} → ", end="")
    
    result = hto.work_task(task)
    
    print(f"{result['status']}")
    
    # 预显示 handoff 前几行
    handoff_preview = result.get('handoff', '')[:150].replace('\n', ' ')
    if handoff_preview:
        print(f"   成果摘要: {handoff_preview}...")

# ====================
# 5. 评审
# ====================

print("\n[4] 方案评审阶段...")
review_tasks = hto.list_tasks(status="REVIEW")
print(f"   待评审任务数: {len(review_tasks)}")

for task in review_tasks:
    print(f"\n   评审: {task['title']}")
    review = hto.review_task(task, reviewer="reviewer")
    
    print(f"     ✓ 通过: {review['approved']}")
    print(f"     ⭐ 评分: {review.get('score', 0):.2f}")
    
    feedback = review.get('feedback', '')[:200]
    if feedback:
        print(f"     反馈: {feedback}...")
    
    if review['approved']:
        hto.complete_task(task)
        print(f"     任务完成！")
    else:
        print(f"     需要返工，重新分配给 data_analyst")
        hto.assign_task(task, assignee="data_analyst")
        # 实际中可能需要再次执行 work_task
        # hto.work_task(task)

# ====================
# 6. 输出最终方案
# ====================

print("\n[5] 生成最终志愿填报方案...")

# 收集所有 DONE 任务
done_tasks = hto.list_tasks(status="DONE")
print(f"   已完成任务: {len(done_tasks)}")

print("\n" + "="*60)
print("【最终志愿填报方案】")
print("="*60)

shared_dir = workspace / "shared"
manifest_path = shared_dir / "manifest.json"

if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text())
    print(f"\n交付物清单（{len(manifest['artifacts'])} 项）：")
    for art in manifest['artifacts']:
        print(f"  - [{art.get('type', 'ITEM')}] {art['path']}")
    
    print("\n方案摘要：")
    for art in manifest['artifacts']:
        art_file = workspace / art['path']
        if art_file.exists():
            content = art_file.read_text()[:300]
            print(f"\n{art['title']}:")
            print(content + "..." if len(art_file.read_text()) > 300 else content)
else:
    print("未找到交付物清单")

print("\n" + "="*60)
print("✅ 志愿填报方案生成完毕！")
print("="*60)

# ====================
# 7. 查看团队状态
# ====================

print("\n[附加] 团队工作负载:")
for agent in team_config.keys():
    status = hto.get_agent_status(agent)
    print(f"  {agent:15s} 角色: {status['role'][:30]:30s} 活跃任务: {status['active_tasks']}")

print("\n所有任务列表:")
for t in hto.list_tasks():
    assignee_display = t.get('assignee', 'unassigned')
    print(f"  [{t['status']:10s}] {t['task_id'][:8]} | {assignee_display:12s} | {t['title'][:40]}")

print("\n完成！")