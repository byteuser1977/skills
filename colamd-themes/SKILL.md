---
name: colamd-themes
description: |
  ColaMD 主题开发与导出工具。用于从网页、Word文档(DOCX)、PDF提取视觉格式并生成v3.0范式CSS主题，
  将Markdown导出为带主题样式的独立HTML或PDF文件，管理内置/自定义主题，验证主题合规性。
  
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

## 前置条件

- Node.js ≥ 18
- 项目路径：`/Volumes/DATA/data/develop/git/ColaMD-themes`
- 首次使用前执行：`cd /Volumes/DATA/data/develop/git/ColaMD-themes && npm install && npm run build`
- CLI命令：`node /Volumes/DATA/data/develop/git/ColaMD-themes/dist/cli.js <command>` 或 `npx tsx /Volumes/DATA/data/develop/git/ColaMD-themes/src/cli.ts <command>`

## 核心工作流

### 工作流1：从源文件提取主题

```bash
# 从网页URL提取
node dist/cli.ts from-url "https://example.com" --name "my-theme"

# 从Word文档提取
node dist/cli.ts from-docx report.docx --name "corporate-theme"

# 从PDF提取
node dist/cli.ts from-pdf paper.pdf --name "academic-theme"

# 自动检测来源类型
node dist/cli.ts extract <source> --name "auto-theme" --auto-match
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
node dist/cli.ts export-html doc.md -t elegant -o output.html

# 单文件导出为PDF
node dist/cli.ts export-pdf doc.md -t dark -o output.pdf

# 批量导出
node dist/cli.ts export docs/*.md --format html -t light -d output/
node dist/cli.ts export docs/ --format pdf -t elegant -d output/
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
node dist/cli.ts set-theme elegant --default

# 注册自定义主题
node dist/cli.ts set-theme my-brand --css themes/swiss-design.css

# 注册并设为默认
node dist/cli.ts set-theme my-brand --css themes/custom.css --default

# 注销自定义主题
node dist/cli.ts set-theme my-brand --remove

# 列出所有主题
node dist/cli.ts list -d themes/

# 验证主题
node dist/cli.ts validate themes/my-theme.css
```

### 工作流4：查询参考信息

```bash
# 列出所有15种色彩系统
node dist/cli.ts color-systems

# JSON格式输出
node dist/cli.ts color-systems -j

# 列出Mermaid预设
node dist/cli.ts mermaid-presets
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
8. PDF 导出：`emulateMediaType('screen')` + `page.pdf()`

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

## 常见任务模式

### 创建品牌主题并导出文档

```bash
# 1. 从企业网站提取基础样式
node dist/cli.ts from-url "https://company.com" --name "brand-theme" --auto-match -o themes/

# 2. 验证生成的主题
node dist/cli.ts validate themes/brand-theme.css

# 3. 注册为主题
node dist/cli.ts set-theme brand-theme --css themes/brand-theme.css --default

# 4. 导出文档
node dist/cli.ts export-html report.md -t brand-theme -o output/report.html
node dist/cli.ts export-pdf report.md -t brand-theme -o output/report.pdf
```

### 批量生成多格式输出

```bash
# 所有 markdown 文件同时导出为 HTML 和 PDF
node dist/cli.ts export docs/*.md --format html -t elegant -d output/html/
node dist/cli.ts export docs/*.md --format pdf -t dark -d output/pdf/
```
