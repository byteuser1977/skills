---
name: colamd-themes
version: 2.0.0
description: |
  ColaMD 主题开发与导出工具 (v0.3.2)。用于从网页、Word文档(DOCX)、PDF提取视觉格式并生成v3.0范式CSS主题，
  将Markdown导出为带主题样式的独立HTML或PDF文件，管理内置/自定义主题，验证主题合规性。
  
  v0.3.2 新增特性：
  - 🔒 SSRF防护 + 输入验证（CSS≤1MB）+ 统一错误处理
  - ⚡ 异步I/O + 模板缓存（LRU, 10个模板, TTL=30min）
  - 🤖 多Agent技能支持（Claude Code/OpenCode/OpenClaw/Hermes/Trae）
  - 🧹 Puppeteer显式资源清理，防止僵尸进程
  
  适用场景：
  - 从URL/DOCX/PDF源提取样式生成CSS主题（from-url, from-docx, from-pdf, extract）
  - 将Markdown文档导出为HTML或PDF并应用主题（export-html, export-pdf, export）
  - 管理和配置主题（set-theme, list）
  - 验证CSS主题是否符合v3.0范式规范（validate）
  - 查询内置色彩系统和Mermaid预设（color-systems, mermaid-presets）
  
  触发关键词：colamd, theme, 主题, CSS主题, Markdown导出, HTML导出, PDF导出, cthemes, colamd-themes
---

# ColaMD Themes Skill

ColaMD v3.0 范式 CSS 主题的生成、验证、导出与管理工具。

**当前支持版本**: @bytechain.cn/colamd-themes **0.3.2**

## 前置条件

- Node.js ≥ 18
- npm 包：`@bytechain.cn/colamd-themes`

### 安装方式（二选一）

**方式1：全局安装（推荐频繁使用）**
```bash
npm install -g @bytechain.cn/colamd-themes
```
安装后直接使用：`colamd-themes <command>` 或 `cthemes <command>`

**方式2：npx 按需运行（无需安装）**
```bash
npx @bytechain.cn/colamd-themes <command>
```

### 首次使用验证
```bash
colamd-themes --version   # 或 npx @bytechain.cn/colamd-themes --version
# 应输出: 0.3.2
```

## 核心工作流

### 工作流1：从源文件提取主题

```bash
# 从网页URL提取
colamd-themes from-url "https://example.com" --name "my-theme"

# 从Word文档提取
colamd-themes from-docx report.docx --name "corporate-theme"

# 从PDF提取
colamd-themes from-pdf paper.pdf --name "academic-theme"

# 自动检测来源类型
colamd-themes extract <source> --name "auto-theme" --auto-match
```

**提取选项：**

| 参数 | 说明 |
|------|------|
| `-n, --name` | 主题名称 |
| `-o, --output` | 输出CSS文件路径 |
| `-d, --themes-dir` | 主题目录（默认：`themes/`） |
| `-c, --color-system` | 强制指定色彩系统ID |
| `-m, --mermaid-preset` | 强制指定Mermaid预设（light/dark/elegant） |
| `-A, --auto-match` | 自动匹配色彩系统和Mermaid预设 |

### 工作流2：导出 Markdown 为 HTML/PDF

```bash
# 单文件导出为HTML
colamd-themes export-html doc.md -t elegant -o output.html

# 单文件导出为PDF
colamd-themes export-pdf doc.md -t dark -o output.pdf

# 批量导出
colamd-themes export docs/*.md --format html -t light -d output/
colamd-themes export docs/ --format pdf -t elegant -d output/
```

**导出选项：**

| 参数 | 说明 |
|------|------|
| `-t, --theme` | 主题：内置名称/自定义注册名/.css文件路径 |
| `-o, --output` | 输出文件路径 |
| `-d, --output-dir` | 批量导出输出目录 |
| `--format` | 格式：`html` 或 `pdf`；PDF支持 `A4`, `Letter`, `A3` |

### 工作流3：主题管理

```bash
# 设置默认主题
colamd-themes set-theme elegant --default

# 注册自定义主题
colamd-themes set-theme my-brand --css themes/swiss-design.css

# 注册并设为默认
colamd-themes set-theme my-brand --css themes/custom.css --default

# 注销自定义主题
colamd-themes set-theme my-brand --remove

# 列出所有主题
colamd-themes list -d themes/

# 验证主题
colamd-themes validate themes/my-theme.css
```

### 工作流4：查询参考信息

```bash
# 列出所有15种色彩系统
colamd-themes color-systems

# JSON格式输出
colamd-themes color-systems -j

# 列出Mermaid预设
colamd-themes mermaid-presets
```

### 工作流5：主题审计与范式验证（增强版）

提取主题后必须进行完整审计，确保字体正确提取、配色合理、背景前景可识别。

#### 5.1 完整审计流程

```bash
# 步骤1：提取主题（启用详细日志记录字体来源）
colamd-themes extract <source> --name "audit-theme" --verbose -o themes/

# 步骤2：基础范式验证
colamd-themes validate themes/audit-theme.css

# 步骤3：全面审计（字体+配色+对比度+图案）
colamd-themes validate themes/audit-theme.css --full-audit

# 步骤4：生成结构化审计报告
colamd-themes validate themes/audit-theme.css --report audit-report.json
```

#### 5.2 字体提取专项审计

**目标**: 验证字体是否从源文件/URL 正确提取并保持一致。

```bash
# 查看字体详细信息
colamd-themes validate theme.css --detail fonts

# 检查各选择器字体一致性
colamd-themes validate theme.css --check font-consistency

# 验证 Web 字体可用性
colamd-themes validate theme.css --check web-fonts
```

**审计要点 (FA 规则)**:

| 规则 | 级别 | 检查内容 |
|------|------|----------|
| FA-01 | MUST | 字体来源可追溯（URL/DOCX/PDF 对应） |
| FA-02 | SHOULD | Web 字体 (@font-face) 加载有效 |
| FA-03 | MUST | 字体回退链完整（≥4级） |
| FA-04 | MUST | **所有选择器字体栈统一**（重点！） |
| FA-05 | SHOULD | 字体文件可用且格式兼容 |

**常见问题**:
- Mermaid 图表 `.node .label` 使用不完整的字体栈
- 代码块缺少等宽字体声明
- 引用块使用不同的字体族

#### 5.3 配色合理性审计

**目标**: 验证配色组合是否合理，特别是背景色与前景元素的识别度。

```bash
# 检查所有背景-前景配对对比度
colamd-themes validate theme.css --check contrast-matrix

# 仅检查代码块可读性
colamd-themes validate theme.css --check code-readability

# 检查 Mermaid 图表配色
colamd-themes validate theme.css --check mermaid-colors
```

**核心审计: 背景前景配对矩阵 (BF-03)**

```
┌─────────────┬───────────┬──────────┬──────────┬──────────┐
│   背景      │  正文文字 │ 次要文字 │ 辅助文字 │  强调色   │
├─────────────┼───────────┼──────────┼──────────┼──────────┤
│ surface     │ ≥7:1 ✅   │ ≥4.5:1✅ │ ≥3:1 ⚠️  │ ≥4.5:1✅ │
│ panel       │ ≥7:1 ✅   │ ≥4.5:1✅ │ ≥3:1 ⚠️  │ ≥4.5:1✅ │
│ panelAlt    │ ≥7:1 ✅   │ ≥4.5:1✅ │ ≥3:1 ⚠️  │ ≥4.5:1✅ │
│ code-bg     │ ≥7:1 ✅   │ N/A      │ N/A      │ N/A      │
│ quote-bg    │ ≥7:1 ✅   │ ≥4.5:1✅ │ N/A      │ N/A      │
└─────────────┴───────────┴──────────┴──────────┴──────────┘
```

**背景类型清单**:
- `--seed-surface`: 页面主背景
- `--seed-panel`: 卡片/面板背景
- `--seed-panelAlt`: 交替行背景
- 代码块背景 (自定义)
- 引用块背景 (自定义)

**前景元素清单**:
- `--seed-ink`: 正文文字
- `--seed-inkMuted`: 次要文字
- `--seed-inkDim`: 辅助文字
- 链接颜色、边框、分割线等

#### 5.4 图案/装饰检测

```bash
# 检测渐变、阴影、背景图等装饰元素
colamd-themes validate theme.css --check patterns

# 检测可能影响阅读的视觉效果
colamd-themes validate theme.css --check visual-interference
```

**检测项 (PT 规则)**:
- PT-01: 渐变背景是否干扰阅读
- PT-02: 背景图片/纹理是否有纯色 fallback
- PT-03: 阴影效果是否过重
- PT-04: 边框装饰是否遮挡内容

#### 5.5 快速诊断命令

```bash
# 仅检查字体问题
colamd-themes validate theme.css --check fonts

# 仅检查对比度
colamd-themes validate theme.css --check contrast

# 检查特定选择器（如 Mermaid 图表）
colamd-themes validate theme.css --selector ".md-diagram-panel"

# 导出可视化 HTML 报告
colamd-themes validate theme.html --visual-report
```

## 主题解析规则

`-t, --theme` 参数支持三种方式：

1. **内置主题**：`light`, `dark`, `elegant`, `newsprint`
2. **自定义注册主题**：通过 `set-theme --css` 注册的名称
3. **文件路径**：任意磁盘上的 `.css` 文件绝对/相对路径

配置文件位置：`~/.colamd-themes/config.json`

## 内置色彩系统（15套）

详见 [references/color-systems.md](references/color-systems.md)

| 色系 | 包含方案 |
|------|----------|
| 莫兰迪 (Morandi) | misty-rose, sage-green, dusky-blue |
| 马卡龙 (Macaron) | strawberry, mint, lavender |
| 北欧 (Nordic) | fjord-blue, pine-green, cloud-grey |
| 复古 (Vintage) | amber, burgundy, forest |
| 薄荷绿 (Mint) | matcha, spearmint, seafoam |

## Mermaid 预设

| 预设 | 说明 |
|------|------|
| `light` | 浅色背景 + 冷色调强调 |
| `dark` | 深色背景 |
| `elegant` | 浅色背景 + 暖色调强调 |

## v3.0 范式约束

生成的CSS必须符合以下约束：

- 选择器中不允许裸 hex 颜色值，必须使用 `var(--seed-*)`
- 不允许裸字体大小，必须使用 `var(--font-*)`
- 不允许 Mermaid SVG 选择器（由内置 `variables.css` 处理）
- `!important` 仅允许在 `@media print` 中使用
- 生成 CSS ≤ 300 行
- 字体栈必须包含 CJK 回退字体并以通用字体族结尾

完整验证规则见 [references/validation-rules.md](references/validation-rules.md)

## 设计约束规范 (DC) ⭐ v2.0

ColaMD 主题生成的**核心设计约束**，确保符合现代中文文档站点标准。

**完整规范**: [references/design-constraints.md](references/design-constraints.md)

### 5 大核心约束速查

| 编号 | 约束域 | 核心规则 |
|------|--------|----------|
| **DC-1** | 字体 | 中文无衬线为主，禁西文主字体；代码等宽+CJK回退 |
| **DC-2** | 字号 | H1→H6: `2/1.5/1.25/1.125/1/0.95` 严格降序（16px基准）|
| **DC-3** | 配色 | 浅色方向；同色相轴明度梯度；禁深底深字/浅底浅字 |
| **DC-4** | 扩展背景 | 与正文同系（浅-浅/深-深），差异≤15% |
| **DC-5** | 打印 | @media print 变量与屏幕版完全一致 |

### 关键代码规范

```css
/* DC-1: 字体 */
--font-body: -apple-system, "PingFang SC", "Hiragino Sans GB",
             "Microsoft YaHei", sans-serif;
--font-code: "SF Mono", "Menlo", "Consolas", "PingFang SC", monospace;

/* DC-3: 配色 - 同色相轴（灰轴）*/
--seed-surface: hsl(0, 0%, 99%);
--seed-panel:   hsl(0, 0%, 96%);
--seed-panelAlt:hsl(0, 0%, 93%);
--seed-border:  hsl(0, 0%, 88%);

/* DC-4: 扩展元素背景 */
.md-code-block { background: #F8F8F8; } /* 比surface暗2-4% */
blockquote       { background: #FAFAFA; } /* 比surface暗1-2% */

/* DC-5: 打印同步 */
@media print {
  :root { --seed-surface: var(--seed-surface); /* 保持原值 */ }
}
```

### 验证命令

```bash
colamd-themes validate theme.css --check design-constraints
colamd-themes validate theme.css --full-audit
```

## 渲染管线架构

导出功能使用 Puppeteer (headless Chromium) + `@bytechain.cn/colamd/renderer`：

```
Source Markdown → Local HTTP Server → Puppeteer → ColaMDEditor → applyTheme → setMarkdown → buildExportHTML → Output
```

关键步骤：
1. 本地 HTTP 服务器提供渲染器 ESM 包（避免 CORS）
2. Puppeteer 导航到服务器页面（同源）
3. `createColaMDEditor({ editable: false })` 初始化 Milkdown 编辑器
4. `applyTheme(name, customCSS?)` 应用主题
5. `setMarkdown(content)` 加载文档内容
6. `ensureAllPluginsRendered()` 等待 Mermaid/KaTeX 渲染完成
7. `buildExportHTML()` → 生成内嵌 CSS 的独立 HTML
8. PDF 导出：使用 `@media print` 规则（非 emulateMediaType），确保 print-color-adjust: exact

## 安全与性能特性 (v0.3.2+)

### 🔒 安全防护

| 特性 | 说明 |
|------|------|
| **SSRF 防护** | URL 提取器验证协议白名单，阻止私有网络访问（防止 Server-Side Request Forgery） |
| **输入验证** | CSS 文件验证扩展名、大小限制（**最大 1MB**）、内容有效性（防止 OOM 攻击） |
| **统一错误处理** | 结构化错误代码 (`CLIError` + `ErrorCode`)，便于调试 |

### ⚡ 性能优化

| 特性 | 说明 |
|------|------|
| **异步 I/O** | 非阻塞文件操作，提升批量导出响应性 |
| **模板缓存** | LRU 缓存策略（最多 10 个模板）、TTL 过期（30 分钟）、基于 mtime 的自动失效 |
| **资源清理** | 显式 Puppeteer 页面清理，防止僵尸进程和内存泄漏 |

## 种子色板模型 (SeedPalette)

v3.0 使用11个种子颜色变量驱动整个主题：

```typescript
interface SeedPalette {
  accent: string;        // 主强调色
  accentLight: string;   // 浅色变体
  accentDark: string;    // 深色变体
  surface: string;       // 页面底色
  panel: string;         // 面板/卡片背景
  panelAlt: string;      // 交替面板背景
  ink: string;           // 正文文字
  inkMuted: string;      // 次要文字
  inkDim: string;        // 辅助/禁用文字
  border: string;        // 边框颜色
  borderStrong: string;  // 强调边框
}
```

## 多 Agent 技能支持

本技能可自动转换为以下 AI 编码代理的格式：

| Agent | 技能路径 | 前置元数据 |
|-------|----------|------------|
| **Claude Code** | `.claude/skills/colamd-themes.skill.md` | `name`, `description` |
| **OpenCode** | `.opencode/skills/colamd-themes/SKILL.md` | `name`, `version`, `user-invocable`, `allowed-tools`, `hooks` |
| **OpenClaw** | `.openclaw/skills/colamd-themes/SKILL.md` | `id`, `name`, `version`, `icon`, `author`, `homepage` |
| **Hermes** | `.hermes/skills/tools/colamd-themes/SKILL.md` | `name`, `version`, `author`, `license`, `tags`, `prerequisites` |
| **Trae** | `.trae/rules/colamd-themes.md` | 纯 Markdown（无前置元数据） |

**构建脚本**:
```bash
npm run build:skills              # 生成所有代理技能
bash skills/build-skills.sh       # 同上
bash skills/build-skills.sh claude # 仅生成 Claude Code
```

## 常见任务模式

### 创建品牌主题并导出文档

```bash
# 1. 从企业网站提取基础样式
colamd-themes from-url "https://company.com" --name "brand-theme" --auto-match -o themes/

# 2. 验证生成的主题
colamd-themes validate themes/brand-theme.css

# 3. 注册为主题
colamd-themes set-theme brand-theme --css themes/brand-theme.css --default

# 4. 导出文档
colamd-themes export-html report.md -t brand-theme -o output/report.html
colamd-themes export-pdf report.md -t brand-theme -o output/report.pdf
```

### 批量生成多格式输出

```bash
# 所有 markdown 文件同时导出为 HTML 和 PDF
colamd-themes export docs/*.md --format html -t elegant -d output/html/
colamd-themes export docs/*.md --format pdf -t dark -d output/pdf/
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `command not found: colamd-themes` | 未全局安装 | 运行 `npm install -g @bytechain.cn/colamd-themes` 或使用 `npx @bytechain.cn/colamd-themes` |
| npx 首次运行非常慢 | 需要下载 npm 包和依赖 | 正常现象，后续运行会使用缓存；频繁使用建议全局安装 |
| PDF 导出失败 / Chromium 错误 | Puppeteer 需要 Chromium | 确保网络可访问，或配置 `PUPPETEER_CHROMIUM_REVISION` 镜像 |
| PDF 提取返回空结果 | PDF 是扫描图像无文本层 | 需要使用有文本层的 PDF（非扫描件） |
| URL 提取失败 | 目标网站反爬或无法访问 | 检查 URL 可访问性，某些 SPA 可能需要额外处理 |
| SSRF 错误 | URL 包含私有网络地址 | 仅允许公网 URL，不支持 localhost/内网地址 |
| CSS 文件过大错误 | 自定义主题超过 1MB 限制 | 压缩或精简 CSS 文件至 1MB 以内 |
| 主题验证显示 MUST 级别错误 | 违反 v3.0 范式约束 | 查看 [references/validation-rules.md](references/validation-rules.md) 对应规则并修复 |
| `set-theme` 配置不生效 | 配置文件路径错误 | 默认配置位于 `~/.colamd-themes/config.json` |
| 内存占用过高 | 批量导出时未释放资源 | v0.3.2+ 已优化，如仍有问题请减少并发数 |

## 版本历史

| 技能版本 | 对应包版本 | 主要变更 |
|----------|------------|----------|
| **2.0.0** | **0.3.2** | **设计约束规范(DC)**：5大核心约束(字体/字号/配色/扩展背景/打印同步) |
| 1.3.0 | 0.3.2 | 增强审计工作流：字体提取验证(FA)、配色合理性审计(CA)、背景前景识别(BF)、图案检测(PT) |
| 1.2.0 | 0.3.2 | 新增安全/性能特性、多Agent支持、SSRF防护 |
| 1.1.0 | 0.3.0 | 初始版本，基于 npm 包重构 |
