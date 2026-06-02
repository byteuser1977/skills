# ColaMD Themes 技能

基于 `@bytechain.cn/colamd-themes` npm 包的 AI Agent 技能（v1.2.0），提供完整的主题生成、验证、导出和管理工作流。

**当前支持 colamd-thems v0.3.2** — 包含安全防护、性能优化和多 Agent 技能支持。

## 🆕 v0.3.2 新特性

### 🔒 安全防护
| 特性 | 说明 |
|------|------|
| **SSRF 防护** | URL 提取器验证协议白名单，阻止私有网络访问 |
| **输入验证** | CSS 文件大小限制（≤1MB）、扩展名检查、内容有效性验证 |
| **统一错误处理** | 结构化错误代码 (`CLIError` + `ErrorCode`)，便于调试 |

### ⚡ 性能优化
| 特性 | 说明 |
|------|------|
| **异步 I/O** | 非阻塞文件操作，提升批量导出响应性 |
| **模板缓存** | LRU 缓存（最多 10 个模板）、TTL 过期（30 分钟）、基于 mtime 自动失效 |
| **资源清理** | 显式 Puppeteer 页面清理，防止僵尸进程和内存泄漏 |

### 🤖 多 Agent 支持

可转换为以下 AI 编码代理的技能格式：
- **Claude Code**
- **OpenCode**
- **OpenClaw**
- **Hermes**
- **Trae**

```bash
# 转换为 Claude Code 技能格式示例
colamd-themes convert-skill --agent claude-code
```

## 快速开始

### 方式1：全局安装（推荐）

```bash
npm install -g @bytechain.cn/colamd-themes

# 验证安装
colamd-themes --version
```

### 方式2：npx 按需运行（无需安装）

```bash
npx @bytechain.cn/colamd-themes <command>
```

### 基本使用示例

```bash
# 从 Word 文档提取并生成主题
colamd-themes extract ./report.docx -n "my-theme" -A

# 从网页提取主题（含 SSRF 防护）
colamd-themes from-url "https://example.com" -n "web-theme"

# 导出 Markdown 为 HTML/PDF（异步 I/O 优化）
colamd-themes export-html doc.md -t elegant -o output.html
colamd-themes export-pdf doc.md -t dark -o output.pdf

# 验证生成的 CSS 主题（含输入验证 ≤1MB）
colamd-themes validate themes/my-theme.css

# 查看可用的色彩系统（15套）
colamd-themes color-systems
```

详细命令参考请查看 [SKILL.md](./SKILL.md)。

## 支持的源格式

| 格式 | 说明 | 命令 |
|------|------|------|
| **URL** | 网页链接，自动解析 CSS 规则（含 SSRF 防护） | `from-url` |
| **DOCX** | Word 文档 (.docx) | `from-docx` |
| **PDF** | 带文本层的 PDF | `from-pdf` |

## 输出格式

| 格式 | 命令 | 优化特性 |
|------|------|----------|
| **CSS** | 主题文件 (v3.0 范式) | `extract` / `from-*` | 输入验证 ≤1MB |
| **HTML** | 独立 HTML 文档 | `export-html` | 异步 I/O + 模板缓存 |
| **PDF** | PDF 文档 | `export-pdf` | Puppeteer 资源清理 |

## 生成的主题结构

CSS 主题文件包含 6 个 SECTION：

1. **Design Tokens** — 种子颜色和字体（用户可编辑）
2. **Semantic Mapping** — 语义变量映射
3. **Mermaid Variables** — 图表配色（20 个变量）
4. **Fine Tuning** — 微调
5. **Selector Adjustments** — 选择器级调整
6. **Print Styles** — 打印样式

## 内置资源

- **4 个内置主题**: `light`, `dark`, `elegant`, `newsprint`
- **15 套色彩系统**: 莫兰迪、马卡龙、北欧、复古、薄荷绿
- **3 套 Mermaid 预设**: `light`, `dark`, `elegant`

详见 [references/color-systems.md](references/color-systems.md)

## 依赖要求

- Node.js ≥ 18
- npm 包: `@bytechain.cn/colamd-themes` (≥ 0.3.2)

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `command not found: colamd-themes` | 运行 `npm install -g @bytechain.cn/colamd-themes` 或使用 `npx @bytechain.cn/colamd-themes` |
| npx 首次运行慢 | 正常现象，首次需要下载包；后续运行会使用缓存 |
| PDF 导出失败 | Puppeteer 需要 Chromium，确保网络可访问或配置镜像 |
| 提取失败 (PDF) | 确认 PDF 有文本层而非扫描图像 |
| 主题验证失败 | 检查 [references/validation-rules.md](references/validation-rules.md) 中的 v3.0 范式约束 |
| CSS 文件过大 ( >1MB ) | v0.3.2 限制 CSS 最大 1MB，请精简或分割主题文件 |
| SSRF 错误 | URL 提取时目标地址被安全策略拦截，请确认 URL 可公开访问 |

## 技能文件结构

```
colamd-themes/
├── SKILL.md                      # 主技能文档（核心指令）
├── manifest.json                 # 元数据与命令定义 (v1.2.0)
├── README.md                     # 本文件
├── scripts/
│   └── colamd-themes-wrapper.sh  # CLI 包装脚本
└── references/
    ├── color-systems.md          # 15 套色彩系统参考
    └── validation-rules.md       # v3.0 范式验证规则
```

## 版本历史

| 技能版本 | 对应 CLI 版本 | 主要变更 |
|----------|---------------|----------|
| **1.2.0** | **0.3.2** | 添加 SSRF 防护、输入验证、异步 I/O、模板缓存、多 Agent 支持特性说明 |
| 1.1.0 | 0.3.x | 初始版本，基于 npm 包重构 |
