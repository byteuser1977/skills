---
name: search-kb
description: Fast full-text search across the knowledge base (1,564 Markdown files, 1M+ lines). Supports fuzzy search, context display, relevance ranking, and caching. Ideal for finding project docs, training materials, and technical manuals.
---

# Search Knowledge Base

High-performance full-text search skill for large Markdown knowledge bases. Supports instant search results with caching, context preview, and relevance ranking.

## When to Use This Skill

Use this skill when you need to:

- Search for specific terms across thousands of documents
- Find project documentation (华夏银行, TATA培训, etc.)
- Locate training materials or technical manuals
- Retrieve historical project records quickly
- Perform keyword-based document discovery

## Quick Start

```bash
# Basic search
npx skills run search-kb "项目管理"

# Search with options
npx skills run search-kb "信贷" --limit 20 --context 3

# Clear cache and rebuild
npx skills run search-kb "Risk Management" --rebuild
```

## Installation

```bash
# Install globally
npx skills add ./skills/search-kb -g

# Or use directly (no install needed)
node skills/search-kb/bin/search-kb.js "your query"
```

## Command-Line Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `keyword` | string | *required* | Search term (supports Chinese/English) |
| `--limit` | number | 50 | Maximum results to display |
| `--context` | number | 2 | Lines before/after match to show |
| `--no-cache` | flag | false | Disable cached index |
| `--rebuild` | flag | false | Force rebuild cache |
| `--help` | flag | - | Show help message |

## Features

### 🚀 Blazing Fast
- First run: builds index (~100-300ms for 1,600 files)
- Subsequent queries: **< 10ms** with cached index
- 7-day cache auto-refresh

### 🔍 Smart Ranking
Results sorted by relevance:
1. Filename matches (highest weight)
2. Path matches (medium weight)
3. Heading/emphasis matches (high weight)
4. Multiple occurrences (low weight)

### 📄 Rich Display
- Yellow highlighting of matched keywords
- Line numbers for easy reference
- 3-line context preview by default
- File path shown relative to knowledge root

### 🧠 Intelligent Caching
- Cache stored in `state/search_cache.json`
- Auto-detects knowledge base modifications
- Minimal memory footprint

## Example Output

```
🔍 搜索关键词: "信贷"
📂 知识库目录: D:\workspace\clawd\knowledge\content\text
⏳ 请稍候...

✅ 使用缓存索引（1603 个文件，更新于 2026/3/11）
🎯 找到 10 个文件包含 "信贷"

───────────────────────────────────────────────────────────────────────────────

📄 2008年神码\华夏综合前置\华夏综合前置\FireFly\doc\交付物\开发\综合前置\01需求\FNS新核心资料\P2 4.应用系统整合方案_信贷管理系统.md (22 处匹配)
   24 |
>>> 25 | - 信贷管理系统
   26 | - 现状
   28 |
>>> 29 | 华夏银行目前所使用的信贷管理系统由企业贷款管理系统和个人贷款管理系统组成，采
   30 |

...
```

## Architecture

```
search-kb/
├── SKILL.md           # Skill documentation (this file)
├── bin/
│   └── search-kb.js   # Main CLI entry point
├── lib/
│   ├── indexer.js     # Build and manage cache index
│   ├── searcher.js    # Full-text search engine
│   └── formatter.js   # Output formatting and highlighting
└── README.md          # Additional notes (optional)
```

## Integration with OpenClaw

This skill integrates seamlessly with OpenClaw agents:

- **Memory recall**: Search results can be stored in MEMORY.md
- **File operations**: Search results can feed into other workflows
- **Batch processing**: Combine with other skills for document processing pipelines

## Performance Tips

1. **Use cache**: Avoid `--no-cache` for interactive use
2. **Limit results**: Use `--limit 20` to reduce output clutter
3. **Context tuning**: `--context 1` for quick scans, `--context 5` for deep reading
4. **Batch queries**: For multiple keywords, run separate queries (cache stays warm)

## Troubleshooting

### "ENOENT: no such file or directory"
Check that `knowledge/content/text` exists and contains `.md` files.

### Slow first run
Initial index build scans all files. Subsequent runs will be fast.

### Cache not updating
Use `--rebuild` to force rebuild. Cache auto-expires after 7 days.

## Changelog

- **v1.0.0** (2026-03-11)
  - Initial release
  - 1,603 file support
  - <10ms cached search
  - Relevance ranking
  - ANSI color highlighting
