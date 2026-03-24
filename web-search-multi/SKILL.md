---
name: web-search-multi
description: Multi-provider web search (Bing + Sogou + Tavily) with parallel execution and result merging. Based on Chatbox's implementation.
---

# Multi-Provider Web Search Skill

完整移植 Chatbox 的 web-search 实现，支持多 provider 并行搜索、交错合并、智能缓存。

## Features

- ✅ Multi-provider: Bing (free) + Sogou (free, CN) + Tavily (paid API, optional)
- ✅ Parallel execution + round-robin merging
- ✅ In-memory cache (5 min TTL)
- ✅ Snippet truncation (150 chars)
- ✅ OpenClaw Tool Calling compatible
- ⚠️ Bing/Sogou are scrapers, rate-limited

## Providers

| Provider | Type | Cost | Quality | Stability | Chinese Support |
|----------|------|------|---------|-----------|-----------------|
| **Bing** | Scraper | Free | High | Medium (anti-scraping) | ✅ via `mkt=zh-CN` |
| **Sogou** | Scraper | Free | Medium | Medium | ✅ Native |
| **Tavily** | API | $0.005/req | High | High | ✅ Native |

**Recommended combinations**:
- Free daily: `["bing"]` (with `mkt=zh-CN`) or `["sogou"]`
- Dual free: `["bing", "sogou"]` (balanced)
- Production: `["tavily"]` or `["bing", "tavily"]`

## Installation

```bash
cd d:\workspace\clawd\skills\web-search-multi
npm install
```

## Usage

### CLI

```bash
# Basic search (default 10 results)
node bin/web-search-multi.js '{"query":"OpenClaw AI","count":10}'

# Use specific providers
node bin/web-search-multi.js '{"query":"如何安装 openclaw","count":10,"providers":["sogou"]}'

# Mixed providers (if Tavily key set)
TAVILY_API_KEY=xxx node bin/web-search-multi.js '{"query":"AI","count":10,"providers":["bing","sogou","tavily"]}'
```

### OpenClaw Integration

Add custom tool in OpenClaw config:

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
              "query": { "type": "string", "description": "Search query" },
              "count": {
                "type": "number",
                "description": "Number of results (1-20)",
                "default": 10,
                "minimum": 1,
                "maximum": 20
              },
              "providers": {
                "type": "array",
                "items": {
                  "type": "string",
                  "enum": ["bing", "sogou", "tavily"]
                },
                "description": "Search providers (default: [\"bing\"]). Options: bing (free), sogou (free CN), tavily (paid)"
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

Restart OpenClaw after config change.

---

## Output Format

```json
{
  "query": "如何安装 openclaw",
  "searchResults": [
    {
      "title": "OpenClaw最新安装指南",
      "snippet": "来源:AI大模型技术栈...",
      "link": "http://mp.weixin.qq.com/s?src=11&...",
      "rawContent": null
    }
  ],
  "total": 9,
  "providers": ["sogou"],
  "duration": 4055,
  "timestamp": 1773634323261
}
```

---

## Implementation Highlights

### Bing `mkt=zh-CN` Parameter

Without `mkt=zh-CN`, Chinese queries on Bing may return garbage/random results due to anti-scraping. Adding this parameter forces Chinese market and ensures quality results.

```javascript
// In BingSearch.js
const params = { q: query, form: 'QBLH', sp: '-1', mkt: 'zh-CN' }
```

### Sogou `.vrwrap` Selector

Based on actual HTML analysis, Sogou search results are contained in `.vrwrap` divs. The provider extracts links from `h3 > a` and resolves `/link?url=` redirects when possible.

```javascript
const resultNodes = dom.querySelectorAll('.vrwrap')
```

### Round-Robin Merging

Results from multiple providers are interleaved to avoid single-provider dominance:

```javascript
for (let i = 0; ; i++) {
  let hasMore = false
  for (const result of results) {
    if (result.items[i]) {
      hasMore = true
      items.push(result.items[i])
    }
  }
  if (!hasMore || items.length >= max) break
}
```

---

## Configuration

`config.json`:

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

Environment variable for Tavily:
```bash
export TAVILY_API_KEY=tvly-xxxx
```

---

## Performance

| Provider | Latency | Cost | Cache TTL | Notes |
|----------|---------|------|-----------|-------|
| Bing | 1-2s | Free | 5 min | Use `mkt=zh-CN` for Chinese |
| Sogou | 4-5s | Free | 5 min | Some links encrypted |
| Tavily | <1s | $0.005/req | 5 min | Most stable |

Caching reduces repeated query latency to <100ms.

---

## Known Issues

1. **Bing link tracking URLs**: Returns `bing.com/ck/a?...` redirect links. Not a problem for user clicks.
2. **Sogou short links**: Some links are encrypted hashes (e.g., `hedJja...`) and cannot be resolved.
3. **Anti-scraping**: Bing/Sogou may block IP if request frequency >10/min. Add delays if needed.
4. **Cross-process cache**: Memory cache is per-process. OpenClaw may spawn new process per tool call, reducing cache effectiveness.

---

## License

MIT

---

**Created**: 2026-03-16
**Version**: 1.1.0 (added Sogou support)
**Based on**: Chatbox web-search implementation
