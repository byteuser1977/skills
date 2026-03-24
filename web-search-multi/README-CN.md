# Multi-Provider Web Search Skill for OpenClaw

完整移植 Chatbox 的 web-search 实现，支持多 provider 并行搜索、交错合并、智能缓存。

## 特性

- ✅ 多 provider 支持（Bing 免费 + Tavily 付费可选）
- ✅ 并行执行 + 交错合并（round-robin）
- ✅ 内存缓存（5分钟 TTL）
- ✅ 摘要截断（150 字符）
- ✅ 与 OpenClaw Tool Calling 无缝集成
- ⚠️ Bing 爬虫可能受反爬影响（建议 <10 req/min）

## Providers

| Provider | 类型 | 成本 | 可用性 |
|---------|------|------|--------|
| **Bing** | 爬虫 | 免费 | ✅ 国内可用 |
| **Tavily** | API | $0.005/次 | ✅ 国内可用 |

**推荐组合**：
- 日常免费：`["bing"]`
- 生产环境：`["tavily"]` 或 `["bing", "tavily"]`

## 安装

```bash
cd d:\workspace\clawd\skills\web-search-multi
npm install
```

## 使用

### CLI 测试

```bash
# 单 provider
node bin/web-search-multi.js '{"query":"OpenClaw AI","count":5,"providers":["bing"]}'

# 多 provider
TAVILY_API_KEY=tvly-xxx node bin/web-search-multi.js '{"query":"AI news","count":10,"providers":["bing","tavily"]}'
```

### OpenClaw 集成

在 OpenClaw 配置文件中添加：

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
              "count": { "type": "number", "description": "结果数量 (1-20)", "default": 5, "minimum": 1, "maximum": 20 },
              "providers": {
                "type": "array",
                "items": { "type": "string", "enum": ["bing", "tavily"] },
                "description": "使用的搜索 provider（默认：["bing"]）"
              }
            },
            "required": ["query"]
          }
        }
      }
    }
  }
}
```

重启后，模型即可调用。

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
  "total": 5,
  "providers": ["bing"],
  "duration": 1689,
  "timestamp": 1773630486364
}
```

## 配置

创建 `config.json`（同目录）：

```json
{
  "providers": ["bing"],
  "maxResults": 10,
  "snippetLength": 150,
  "cacheTtlMinutes": 5,
  "tavily": {
    "apiKey": null,
    "searchDepth": "basic",
    "maxResults": 5,
    "timeRange": null,
    "includeRawContent": null
  }
}
```

或通过环境变量：
```bash
export TAVILY_API_KEY=tvly-xxxx
```

## 工作原理

### 并行 + 交错合并

```javascript
// 并行执行所有 provider
const results = await Promise.allSettled(
  providers.map(p => p.search(query, signal))
)

// 交错合并（round-robin）
let i = 0, hasMore = false
do {
  hasMore = false
  for (const result of results) {
    // 只取成功的结果
    if (result.status === 'fulfilled' && result.value.items[i]) {
      hasMore = true
      items.push(result.value.items[i])  // 轮流取第 i 条
    }
  }
  i++
} while (hasMore && items.length < MAX)
```

### 缓存

```javascript
const key = `search-context:${query}`
if (cache.has(key) && !expired) {
  return cache.get(key)
}
const result = await multi.search(query)
cache.set(key, { result, timestamp: Date.now() })
```

默认 TTL：5 分钟

## 文件结构

```
web-search-multi/
├── SKILL.md
├── README.md | README-CN.md
├── package.json
├── config.json
├── src/
│   ├── base.js
│   ├── BingSearch.js
│   ├── TavilySearch.js
│   ├── MultiSearch.js
│   ├── MemoryCache.js
│   ├── truncate.js
│   └── index.js
├── bin/
│   └── web-search-multi.js
└── test/
    └── input.json
```

## 扩展新 Provider

1. 创建 `src/NewProvider.js`，继承 `BaseSearch`
2. 实现 `async executeSearch(query, signal)`，返回 `{ items: [...] ] }`
3. 在 `src/index.js` 的 `tool.execute` 中添加 case
4. 更新 `config.json` 和 `package.json` 配置

## 错误处理

- 单个 provider 失败：返回空数组，不影响其他
- 全部失败：返回空结果（不抛错）
- 超时：通过 AbortSignal 控制
- 反爬：建议降低频率，添加延迟（未实现）

## 成本估算

- Bing：免费（但需注意反爬风险）
- Tavily：$0.005/次（约 0.035 元/次）

启用缓存可显著降低 API 调用次数。

## Testing

```bash
npm test
# 或
node bin/web-search-multi.js '{"query":"OpenClaw","count":5}'
```

---

**Created**: 2026-03-16
**Version**: 1.0.0
**License**: MIT
