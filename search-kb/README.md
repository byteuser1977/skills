# Search Knowledge Base Skill

高性能全文搜索技能，专为 OpenClaw 知识库设计。

---

## 🚀 快速开始

### 基础搜索

```bash
# 最简单的用法：搜索关键词
search-kb "项目管理"

# 查看帮助
search-kb --help
```

### 常用示例

```bash
# 搜索中文关键词
search-kb "信贷" --limit 10

# 搜索英文术语（不区分大小写）
search-kb "Risk Management" --limit 20 --context 3

# 快速浏览（上下文更少）
search-kb "支付系统" --context 1

# 深度查看（上下文更多）
search-kb "投资银行" --context 5 --limit 5
```

---

## 📦 安装

### 方法 A：全局安装（推荐）

```bash
# 安装到所有用户
npx skills add ./skills/search-kb -g -y

# 或指定 agent
npx skills add ./skills/search-kb -a openclaw -y
```

### 方法 B：项目级使用

```bash
cd D:\workspace\clawd
npx skills add ./skills/search-kb
```

### 方法 C：直接运行（无需安装）

```bash
node ./skills/search-kb/bin/search-kb.js "关键词"
```

---

## ⚙️ 命令行选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `keyword` | 字符串 | **必填** | 搜索关键词（支持中文/英文） |
| `--limit <N>` | 数字 | 50 | 最多显示 N 个结果 |
| `--context <N>` | 数字 | 2 | 显示匹配行前后各 N 行 |
| `--no-cache` | 标志 | false | 禁用缓存（慢） |
| `--rebuild` | 标志 | false | 强制重建缓存 |
| `--filter-dir <path>` | 字符串 | null | 只搜索指定目录（相对知识库根） |
| `--min-size <KB>` | 数字 | 0 | 只搜索文件大小 ≥ N KB 的文件 |
| `--max-size <KB>` | 数字 | ∞ | 只搜索文件大小 ≤ N KB 的文件 |
| `--output <format>` | json/csv/text | text | 输出格式 |
| `--help, -h` | 标志 | - | 显示帮助 |

---

## 🎯 输出说明

### 默认文本输出

```
🎯 找到 10 个文件包含 "信贷"
───────────────────────────────────────────────────────────────────────────────

📄 2008年神码\华夏综合前置\华夏综合前置\FireFly\doc\交付物\开发\综合前置\01需求\FNS新核心资料\P2 4.应用系统整合方案_信贷管理系统.md (22 处匹配)
   24 |
>>> 25 | - 信贷管理系统
   26 | - 现状
   28 |
>>> 29 | 华夏银行目前所使用...

───────────────────────────────────────────────────────────────────────────────
📊 搜索结果总计: 10 个文件
```

### JSON 输出（用于编程）

```bash
search-kb "项目管理" --output json --limit 2
```

```json
{
  "query": "项目管理",
  "timestamp": "2026-03-11T09:41:00.000Z",
  "totalFiles": 1603,
  "results": [
    {
      "path": "D:/workspace/clawd/knowledge/content/text/2008年神码/...",
      "relativePath": "2008年神码\\...",
      "name": "项目经理手册V2.0.md",
      "size": 46080,
      "matchCount": 156,
      "bestScore": 135,
      "matches": [
        { "line": 45, "text": "项目管理规范要求..." },
        { "line": 78, "text": "项目管理系统使用指南..." }
      ]
    }
  ]
}
```

---

## ⚡ 性能

| 操作 | 耗时 (1,603 文件) | 说明 |
|------|-------------------|------|
| 首次索引 | ~200 ms | 扫描所有文件并生成缓存 |
| 后续查询 | < 10 ms | 使用缓存，近实时 |
| 缓存过期 | 7 天 | 自动重建索引 |

**建议：**
- ✅ 首次查询稍慢，之后极快
- ✅ 缓存文件 `state/search_cache.json` ~80 KB
- ✅ 内存占用 < 50 MB

---

## 🛠️ 高级功能

### 过滤目录

只搜索特定分类（如 TATA 培训资料）：

```bash
search-kb "风险管理" --filter-dir "TATA/File/资料/Academy Certification/Risk Management"
```

### 过滤文件大小

排除过小或过大的文件：

```bash
# 只搜索 10KB-100KB 的文件
search-kb "架构" --min-size 10 --max-size 100
```

### 批量搜索脚本

```bash
@echo off
set keywords=项目管理 信贷 风险管理 支付系统
for %%k in (%keywords%) do (
    echo ==== 搜索: %%k ====
    search-kb "%%k" --limit 5 --output json > "results_%%k.json"
)
```

---

## 🔧 故障排除

### "缓存文件损坏"
```bash
search-kb "test" --rebuild
```

### "找不到知识库文件"
确保 `knowledge/content/text` 目录存在且包含 `.md` 文件。

### "输出乱码"
如果终端不支持 ANSI 颜色，使用：
```bash
search-kb "test" --output text
```

或设置环境变量：
```bash
set NO_COLOR=1
search-kb "test"
```

---

## 📊 与其他工具的集成

### 1. 结合 `find` 或 `grep`（Windows/Linux）

```bash
# 先搜索，再用 grep 过滤
search-kb "payment" --output json | grep -i "bank"
```

### 2. 导入到 Excel/CSV

```bash
# 生成 CSV 报告
search-kb "credit" --output csv > credit_report.csv
```

### 3. 与 OpenClaw Agent 协作

Agent 可以自动调用此技能，将搜索结果写入 `MEMORY.md` 或生成摘要。

---

## 🤝 贡献

本技能为 OpenClaw 生态的一部分。如需增强功能：

1. Fork 本技能目录
2. 修改 `lib/` 下模块
3. 更新 `SKILL.md` 文档
4. 提交 PR 或本地测试

---

## 📄 许可证

MIT © 2026 OpenClaw Community

---

**最后更新：** 2026-03-11
**版本：** 1.0.0
**知识库规模：** 1,603 文件，45+ MB
