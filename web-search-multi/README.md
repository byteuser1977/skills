# Multi-Provider Web Search Skill for OpenClaw

完整移植 Chatbox 的 web-search 实现，支持多 provider 并行搜索、交错合并、智能缓存。

## 快速开始

### 安装依赖

```bash
cd d:\workspace\clawd\skills\web-search-multi
npm install
```

### 命令行测试

```bash
# 测试搜索（默认 10 条结果）
node bin/web-search-multi.js '{"query":"OpenClaw AI","count":10}'

# 指定 providers（Bing 免费，Sogou 免费国内，Tavily 付费）
TAVILY_API_KEY=your_key node bin/web-search-multi.js '{"query":"AI news","count":10,"providers":["bing","sogou","tavily"]}'
```

### OpenClaw 集成

在 OpenClaw 配置文件中添加自定义工具：

```json5
{
  "tools": {
    "web": {
      "search": {
        "enabled": true,
        "provider": "custom",
        "custom": {
          "command": "node d:/workspace/clawd/skills/web-search-multi/bin/web-search-multi.js",
          "schema": {
            "type": "object",
            "properties": {
              "query": { "type": "string", "description": "搜索关键词" },
              "count": { "type": "number", "description": "返回结果数量 (1-20)", "default": 10, "minimum": 1, "maximum": 20 },
              "providers": {
                "type": "array",
                "items": {
                  "type": "string",
                  "enum": ["bing", "sogou", "tavily"]
                },
                "description": "搜索提供商列表。可选：bing (免费)、sogou (免费，国内)、tavily (付费 API)。默认：[\"bing\"]"
              }
            },
            "required": ["query"]
          }
        }
      }
    }
  }
```

重启 OpenClaw 后，模型即可通过函数调用使用该技能。

## 特性

| 特性 | 说明 |
|------|------|
| **多 provider** | Bing（免费爬虫）+ Sogou（免费爬虫，国内可用）+ Tavily（付费 API，可选） |
| **并行执行** | 所有 provider 并发请求，降低总延迟 |
| **交错合并** | Round-robin 方式混合结果，避免单一 provider 主导 |
| **智能缓存** | 内存缓存（5分钟 TTL），减少重复请求 |
| **摘要截断** | 统一 snippet 长度（默认 150 字符） |
| **错误隔离** | 单个 provider 失败不影响其他结果 |
| **可配置** | providers、maxResults、snippetLength、cacheTtl |

## 输出格式

```json
{
  "query": "OpenClaw AI",
  "searchResults": [
    {
      "title": "...",
      "snippet": "...",
      "link": "https://...",
      "rawContent": null
    }
  ],
  "total": 10,
  "providers": ["bing"],
  "duration": 1234,
  "timestamp": 1234567890
}
```

## Providers 对比

| Provider | 类型 | 成本 | 质量 | 稳定性 | 中文支持 | 限制 |
|---------|------|------|------|--------|---------|------|
| **Bing** | 爬虫 | 免费 | 高 | 中（可能被反爬） | ✅ 使用 `mkt=zh-CN` 参数 | 建议 <10 req/min |
| **Sogou** | 爬虫 | 免费 | 中 | 中（国内可用） | ✅ 原生中文 | 部分链接加密 |
| **Tavily** | API | $0.005/次 | 高 | 高 | ✅ 原生支持 | 支持全文提取 |

**推荐组合**：
- **日常免费使用**: `["bing"]`（添加 `mkt=zh-CN`）或 `["sogou"]`（纯国内）
- **混合双保险**: `["bing", "sogou"]`（两个免费源）
- **企业生产**: `["tavily"]` 或 `["bing", "tavily"]`
- **最大覆盖**: `["bing", "sogou", "tavily"]`（三者并行）

---

## Bing 中文搜索优化

Bing 爬虫默认根据 IP 判断市场，可能导致中文查询返回垃圾结果。本技能通过 `mkt=zh-CN` 参数**强制中文市场**，确保中文搜索质量。

**测试**：
```bash
node bin/web-search-multi.js '{"query":"如何安装 openclaw","count":10,"providers":["bing"]}'
# 返回 10 条高质量中文结果
```

---

## Sogou 中文搜索

Sogou 作为国内搜索引擎，对中文搜索有天然优势：
- ✅ 无 IP 地域限制（国内即中文）
- ✅ 结果包含微信、头条、百科等中文生态
- ⚠️ 部分链接经过加密（短链接），可能无法直接访问
- ⚠️ 反爬机制（建议低频使用）

**测试**：
```bash
node bin/web-search-multi.js '{"query":"如何安装 openclaw","count":10,"providers":["sogou"]}'
# 返回 9-10 条中文结果（微信公众号、知乎、B站等）
```

---

## 配置

创建 `config.json`（同目录）：

```json
{
  "providers": ["bing", "sogou"],
  "maxResults": 10,
  "snippetLength": 150,
  "cacheTtlMinutes": 5,
  "tavily": {
    "apiKey": null,
    "searchDepth": "basic",
    "maxResults": 10,
    "timeRange": null,
    "includeRawContent": null
  }
}
```

或通过环境变量：
```bash
export TAVILY_API_KEY=tvly-xxxx
```

---

## 工作原理

### 并行与交错合并

参考 Chatbox 的 `_searchRelatedResults`：

```javascript
// 1. 并行执行所有 provider
const results = await Promise.allSettled(
  providers.map(p => p.search(query, signal))
)

// 2. 交错合并（round-robin）
let i = 0, hasMore = false
do {
  hasMore = false
  for (const result of results) {
    if (result.items[i]) {
      hasMore = true
      items.push(result.items[i])  // 轮流取第 i 条
    }
  }
  i++
} while (hasMore && items.length < MAX)
```

### 缓存机制

```javascript
const key = `search-context:${query}`
if (cache.has(key) && !expired) {
  return cache.get(key)
}
const result = await multi.search(query)
cache.set(key, { result, timestamp: Date.now() })
```

默认 TTL：5 分钟

---

## File Structure

```
web-search-multi/
├── SKILL.md
├── README.md
├── package.json
├── config.json (optional)
├── src/
│   ├── base.js              # Abstract BaseSearch class
│   ├── BingSearch.js        # Bing provider (mkt=zh-CN)
│   ├── SogouSearch.js       # Sogou provider (国内中文)
│   ├── TavilySearch.js      # Tavily provider (API)
│   ├── MultiSearch.js       # Orchestrator (parallel + interleave)
│   ├── MemoryCache.js       # TTL cache
│   ├── truncate.js          # Snippet truncation
│   └── index.js             # Tool definition
├── bin/
│   └── web-search-multi.js  # CLI wrapper
└── test/
    └── input.json
```

---

## 扩展新 Provider

1. 创建 `src/NewProvider.js`，继承 `BaseSearch`
2. 实现 `async executeSearch(query, signal)`，返回 `{ items: [...] }`
3. 在 `src/index.js` 的 `tool.execute` 中添加 case
4. 更新 `config.json` 和 `package.json` 配置

示例：

```javascript
import { BaseSearch } from './base.js'
import { parse } from 'node-html-parser'

export class MySearch extends BaseSearch {
  async executeSearch(query, signal) {
    const html = await this.fetch('https://example.com/search?q=' + encodeURIComponent(query), { signal })
    const dom = parse(html)
    // ... extract items
    return { items: [...] }
  }
}
```

---

## 错误处理

- **单个 provider 失败**：捕获异常，返回 `{ items: [] }`，不影响其他 provider
- **全部失败**：返回空结果（不抛错），允许模型根据上下文处理
- **超时**：通过 AbortSignal 控制，默认 30 秒
- **反爬**：建议 <10 次/分钟（Bing/Sogou）

---

## 性能与成本

| Provider | 延迟 | 成本 | 缓存效果 |
|---------|------|------|----------|
| Bing | 1-2s | 免费 | 高（5分钟避免重复） |
| Sogou | 4-5s | 免费 | 高 |
| Tavily | <1s | $0.005/次（约 0.035 元/次） | 中 |

**建议**：
- 启用缓存，避免相同查询重复请求
- 生产环境优先 Tavily（稳定性高）
- 设置合理 `count`（通常 10 足够）

---

## Testing

```bash
# Install deps
npm install

# Chinese test (Bing + mkt)
node bin/web-search-multi.js '{"query":"如何安装 openclaw","count":10,"providers":["bing"]}'

# Chinese test (Sogou)
node bin/web-search-multi.js '{"query":"如何安装 openclaw","count":10,"providers":["sogou"]}'

# English test
node bin/web-search-multi.js '{"query":"how to install openclaw","count":10}'

# Mixed providers (if Tavily configured)
TAVILY_API_KEY=xxx node bin/web-search-multi.js '{"query":"OpenClaw","count":10,"providers":["bing","sogou","tavily"]}'
```

---

## License

MIT

---

## Credits

- **Chatbox**: Original implementation in TypeScript
- **OpenClaw**: Skill framework and tool calling integration
- **Bing**: Search engine (unofficial scraping, mkt=zh-CN for Chinese)
- **Sogou**: Chinese search engine (www.sogou.com)
- **Tavily**: Search API for AI agents

---

**Created**: 2026-03-16
**Updated**: 2026-03-16 (added Sogou support)
**Version**: 1.1.0
