---
name: colamd-themes
version: 1.0.0
description: ColaMD 主题生成与管理技能，基于 ColaMD-themes CLI 工具。支持从 URL、DOCX、PDF 提取视觉格式并转换为符合 v3.0 范式的 CSS 主题文件，包含 WCAG 对比度验证、自动颜色系统匹配、Mermaid 预设等功能。
---

# ColaMD Themes 技能

## 概述

ColaMD-themes 是一个专业的主题开发工具包，用于从现有文档或网页提取视觉设计，并转换成 ColaMD 编辑器兼容的 CSS 主题文件。该技能提供完整的命令行接口，支持自动化工作流。

## 核心能力

- **多源提取**：从 URL、DOCX、PDF 提取排版样式（字体、大小、颜色、行高）
- **v3.0 范式**：基于 5 种种子颜色 + 3 种字体栈的紧凑主题生成（≤300 行）
- **WCAG 验证**：自动检查对比度合规性（AAA/AA 标准）
- **智能配色**：15 种内置颜色系统（Morandi、Macaron、Nordic 等）
- **Mermaid 集成**：20 种图表变量自动生成
- **主题管理**：列表、验证、预览、批量比较
- **打印优化**：自动生成打印样式，确保屏幕-打印一致性

## 环境要求

- **Node.js** ≥ 18
- **项目路径**：必须在 ColaMD-themes 项目根目录下运行，或者通过 NPX 调用
- **工作目录**：`/mnt/d/workspace/git/ColaMD-themes`（项目根目录）

## 安装与部署

```bash
# 进入项目目录
cd /mnt/d/workspace/git/ColaMD-themes

# 安装依赖
npm install

# 编译 TypeScript（生成 dist/ 目录）
npm run build

# 验证安装（查看帮助）
npx tsx src/cli.ts --help
# 或使用编译后的版本
npm run start -- --help
```

## 技能命令

### 1. 提取主题（三种源类型）

#### 从 URL 提取
```bash
npx tsx src/cli.ts from-url <URL> [options]
# 示例：npx tsx src/cli.ts from-url "https://developer.mozilla.org" -n "mdn-theme"
```

#### 从 DOCX 提取
```bash
npx tsx src/cli.ts from-docx <file.docx> [options]
# 示例：npx tsx src/cli.ts from-docx report.docx -n "corporate-theme" --auto-match
```

#### 从 PDF 提取
```bash
npx tsx src/cli.ts from-pdf <file.pdf> [options]
# 示例：npx tsx src/cli.ts from-pdf paper.pdf -n "academic-theme" --color-system sage-green
```

#### 自动检测源类型
```bash
npx tsx src/cli.ts extract <source> [options]
# 示例：npx tsx src/cli.ts extract ./docs/Brand-Guide.docx -n "brand-theme" -A
```

### 2. 列表与查询

```bash
# 列出已生成的主题
npx tsx src/cli.ts list

# 列出内置颜色系统（15 种）
npx tsx src/cli.ts color-systems
npx tsx src/cli.ts color-systems --json  # JSON 格式

# 列出 Mermaid 预设（3 种：light/dark/elegant）
npx tsx src/cli.ts mermaid-presets
npx tsx src/cli.ts mermaid-presets --json
```

### 3. 验证主题
```bash
npx tsx src/cli.ts validate <theme.css>
# 示例：npx tsx src/cli.ts validate themes/my-theme.css
```
验证规则包括：
- 对比度（CR-01~06）：ink:surface ≥ 7:1 (AAA), accent:surface ≥ 4.5:1 (AA)
- 色相和谐（HR-01~03）：强调色饱和度 ≥ 0.30，最多 2 个高饱和色相
- 饱和度约束（SL-01~04）：表面饱和度 ≤ 0.05，代码块背景 ≤ 0.10
- 中性轴（NT-01~03）：文字颜色使用同色轴，亮度差渐变
- 字体规则（FP/FS 系列）：≤ 4 种字体，标题比例递减，包含 CJK 回退
- 表面层级（SH-01~03）：相邻表面亮度差 ≥ 0.04
- 边框规则（BD-01~03）：边框饱和度 ≤ 0.05
- 映射禁止（MP-01~05）：text-color 必须为 seed-ink，bg-color 必须为 seed-surface

## 提取选项

所有提取命令支持以下通用选项：

| 选项 | 描述 |
|------|------|
| `-n, --name <name>` | 主题名称（默认从源文件名或 URL 标题生成） |
| `-o, --output <path>` | 输出 CSS 文件路径（默认：`themes/<name>.css`） |
| `-d, --themes-dir <dir>` | 主题输出目录（默认：`themes/`） |
| `-c, --color-system <id>` | 强制使用指定颜色系统（使用 `color-systems` 查看可用 ID） |
| `-m, --mermaid-preset <id>` | 强制使用指定 Mermaid 预设（light/dark/elegant） |
| `-A, --auto-match` | 自动匹配颜色系统和 Mermaid 预设（推荐） |

## v3.0 范式核心原则

生成的 CSS 主题必须遵循这些约束：

1. **仅使用变量**：所有颜色和字体大小必须通过 `var(--seed-*)` 和 `var(--font-*)` 引用，禁止裸值
2. **变量优先**：修改主题只需调整 SECTION 1 的种子变量（11 个颜色 + 4 个字体栈）
3. **Mermaid 分离**：禁止在主题文件中写入 SVG 选择器（由 ColaMD 内置 `variables.css` 处理）
4. **打印样式**：`@media print` 块中使用 `!important` 保证打印一致性
5. **文件大小**：输出 CSS 不超过 300 行（约 568 行模板压缩后）
6. **CJK 支持**：所有字体栈必须包含中文字体回退并以通用族结尾

## 颜色系统（15 种方案）

| 家族 | 方案 | 风格描述 |
|------|------|----------|
| 莫兰迪 (Morandi) | misty-rose, sage-green, dusky-blue | 低饱和度，柔和优雅 |
| 马卡龙 (Macaron) | strawberry, mint, lavender | 高亮度，甜蜜粉彩色 |
| 北欧 (Nordic) | fjord-blue, pine-green, cloud-grey | 干净极简，冷色调 |
| 复古 (Vintage) | amber, burgundy, forest | 温暖丰富，怀旧感 |
| 薄荷绿 (Mint Green) | matcha, spearmint, seafoam | 清新现代，绿色系 |

使用 `color-systems --json` 获取完整配色细节。

## 典型工作流

### 工作流 1：从源生成并验证
```bash
# 1. 自动提取并匹配配色
npx tsx src/cli.ts extract source.docx -n "my-theme" -A

# 2. 查看生成的主题
cat themes/my-theme.css

# 3. 验证合规性
npx tsx src/cli.ts validate themes/my-theme.css

# 4. 如有问题，只修改 SECTION 1 的种子变量，然后重新验证
```

### 工作流 2：强制使用特定颜色系统
```bash
# 提取时保留源排版，但强制使用 Morandi 配色
npx tsx src/cli.ts from-url https://example.com -n "example-morandi" --color-system sage-green

# 预览效果后，如需微调，编辑 themes/example-morandi.css 的 SECTION 1
```

### 工作流 3：列表与批量审计
```bash
# 列出所有主题
npx tsx src/cli.ts list

# 批量验证（脚本示例）
for theme in themes/*.css; do
  echo "Validating $theme..."
  npx tsx src/cli.ts validate "$theme" || echo "FAILED: $theme"
done
```

## 输出 CSS 结构

生成的主题文件分为 6 个 SECTION：

```
SECTION 1 — Design Tokens (用户可编辑)
  1.1 Seed Palette (11 变量: accent/surface/panel/panel-alt/ink 及其变体)
  1.2 Typography (4 字体栈: body/heading/code/mermaid)
  1.3 Font Sizing (12 变量: 标题 1-6、正文字号等)
  1.4 Radii & Spacing (圆角、间距)

SECTION 2 — Semantic Mapping (自动派生)
  2.1 Surface  2.2 Text  2.3 Links/Accent
  2.4 Borders  2.5 Inline Code  2.6 Code Blocks
  2.7 Blockquote  2.8 Tables  2.9 Scrollbar

SECTION 3 — Mermaid 20 Core Variables
  3.1 Container  3.2 Font  3.3 Nodes  3.4 Edges
  3.5 Clusters  3.6 Labels  3.7 Titles/Axes
  3.8 Person Nodes  3.9 Label Offset

SECTION 4 — Fine Tuning
SECTION 5 — Selector Micro Adjustments
SECTION 6 — @media print
```

## 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| `Cannot find module` | 未运行 `npm install` 或未编译 | 运行 `npm install && npm run build` |
| 提取失败/样式缺失 | 源文件/网页不可访问或格式异常 | 检查源路径，确保网络可达，PDF 要求文本层（非扫描图像） |
| 颜色系统匹配失败 | `color-systems` 数据缺失 | 确保 `src/color-systems.ts` 存在且编译成功 |
| Mermaid 预设未应用 | 未使用 `--auto-match` 或未指定 `--mermaid-preset` | 使用 `-A` 选项或手动设置 `-m <preset>` |
| 验证报 MUST 错误 | 对比度或饱和度不达标 | 调整 SECTION 1 的种子颜色亮度/饱和度，或更换颜色系统 |
| 编译错误（TS） | TypeScript 版本不匹配 | 确保 TypeScript ≥ 5.5（devDependencies 指定） |

## 调试提示

- 使用 `npm run dev` 启动热重载模式直接运行 `src/cli.ts`（无需编译）
- 查看 `src/validators.ts` 了解所有 15+ 验证规则（CR/HR/SL/NT/FP/FS/SH/BD/MP 系列）
- 参考 `src/templates/theme-paradigm.md` 获取完整的 v3.0 规范说明
- 内置演示内容在 `src/preview/demo-content.md`（预览技能使用）

## 与预览技能配合使用

本项目配套提供预览技能（见 `.claude/skills/colamd-themes-preview.skill.md`），功能包括：
- `generate <theme.css>` — 生成交互式 HTML 预览
- `compare <theme1> <theme2>...` — 多主题批量对比
- `serve` — 开发服务器（热重载）
- `audit <theme.css> --type <document|design|ppt>` — 针对文档类型的专项审计

典型组合：
```bash
# 提取主题
npx tsx src/cli.ts extract source.docx -n "report-theme" -A

# 预览效果（在另一个终端）
npx tsx src/preview/preview-server.ts -w themes/

# 审计合规性（针对文档类型）
npx tsx src/preview/generate-html.ts themes/report-theme.css --audit --type document
```

## 限制与约束

- **源文件大小**：URL 提取限制为页面的 CSS 规则数量（大页面可能截断）
- **PDF 要求**：需要文本层的 PDF；扫描版需额外 OCR 依赖（未内置）
- **字体回退**：生成的主题自动包含 CJK 回退，但需系统有对应字体才能完全渲染
- **命令行模式**：仅在项目根目录运行（依赖 `src/` 和 `templates/` 相对路径）
- **Node.js 版本**：≥ 18（使用现代 ES 模块和 fetch API）

## 更新与维护

如需修改行为，编辑源代码后重新编译：
```bash
# 编辑 TypeScript 文件
vim src/cli.ts  # 或其他源文件

# 重新编译
npm run build

# 测试
npx tsx src/cli.ts list
```

主要源码文件：
- `src/cli.ts` — Commander.js CLI 入口，所有子命令路由
- `src/extractors/` — 三种提取器实现（url-extractor.ts, docx-extractor.ts, pdf-extractor.ts）
- `src/docx-style-paradigm.ts` — 核心范式引擎（字体层次、标准预设、WCAG 工具）
- `src/contrast.ts` — WCAG 2.1 对比度计算
- `src/validators.ts` — 15+ 范式验证规则
- `src/color-systems.ts` — 12 种配色方案定义
- `src/mermaid-presets.ts` — Mermaid 变量预设
- `src/generator.ts` — Handlebars 渲染管线
- `src/templates/theme-template.hbs` — 主题模板（~568 行）
- `src/templates/theme-paradigm.md` — v3.0 范式规范文档

## 资源目录说明

本技能目录结构：
- **SKILL.md** — 本技能文档（命令参考、工作流、故障排除）
- **scripts/** — 可选的使用示例脚本
- **references/** — API 和范式详细参考（可选）
- **assets/** — 模板或配置文件（当前为空）

---

## 快速命令速查

```bash
# 提取（推荐自动匹配）
npx tsx src/cli.ts extract <source> -n <name> -A

# 验证
npx tsx src/cli.ts validate themes/<name>.css

# 列出发可用配色
npx tsx src/cli.ts color-systems

# 列出所有生成的主题
npx tsx src/cli.ts list
```

## 相关链接

- 项目文档：`README.md`（同目录）
- 范式规范：`src/templates/theme-paradigm.md`
- AI 技能（Claude）：`.claude/skills/colamd-themes.skill.md`
- 预览技能：`.claude/skills/colamd-themes-preview.skill.md`
