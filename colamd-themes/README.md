# ColaMD Themes 技能

基于 `@bytechain.cn/colamd-themes` npm 包的 AI Agent 技能，提供完整的主题生成、验证、导出和管理工作流。

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

# 从网页提取主题
colamd-themes from-url "https://example.com" -n "web-theme"

# 导出 Markdown 为 HTML/PDF
colamd-themes export-html doc.md -t elegant -o output.html
colamd-themes export-pdf doc.md -t dark -o output.pdf

# 验证生成的 CSS 主题
colamd-themes validate themes/my-theme.css

# 查看可用的色彩系统（15套）
colamd-themes color-systems
```

详细命令参考请查看 [SKILL.md](./SKILL.md)。

## 支持的源格式

| 格式 | 说明 | 命令 |
|------|------|------|
| **URL** | 网页链接，自动解析 CSS 规则 | `from-url` |
| **DOCX** | Word 文档 (.docx) | `from-docx` |
| **PDF** | 带文本层的 PDF | `from-pdf` |

## 输出格式

| 格式 | 命令 |
|------|------|
| **CSS** | 主题文件 (v3.0 范式) | `extract` / `from-*` |
| **HTML** | 独立 HTML 文档 | `export-html` |
| **PDF** | PDF 文档 | `export-pdf` |

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
- npm 包: `@bytechain.cn/colamd-themes`

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `command not found: colamd-themes` | 运行 `npm install -g @bytechain.cn/colamd-themes` 或使用 `npx @bytechain.cn/colamd-themes` |
| npx 首次运行慢 | 正常现象，首次需要下载包；后续运行会使用缓存 |
| PDF 导出失败 | Puppeteer 需要 Chromium，确保网络可访问或配置镜像 |
| 提取失败 (PDF) | 确认 PDF 有文本层而非扫描图像 |
| 主题验证失败 | 检查 [references/validation-rules.md](references/validation-rules.md) 中的 v3.0 范式约束 |

## 技能文件结构

```
colamd-themes/
├── SKILL.md                      # 主技能文档（核心指令）
├── manifest.json                 # 元数据与命令定义
├── README.md                     # 本文件
├── scripts/
│   └── colamd-themes-wrapper.sh  # CLI 包装脚本
└── references/
    ├── color-systems.md          # 15 套色彩系统参考
    └── validation-rules.md       # v3.0 范式验证规则
```
