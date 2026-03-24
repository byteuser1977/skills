# Skills 技能库

本仓库包含多个实用的自动化技能，用于文档处理、数据搜索、知识库管理和网页搜索等场景。

## 📚 技能列表

### 1. document-organizer - 文档整理技能
专业的文档批量处理技能，支持旧版 Office 文档（.doc/.xls）高质量转换为 Markdown，保持格式结构完整。

**核心能力：**
- Word/Excel/PowerPoint 文档转换为 Markdown
- 批量处理，保持原目录结构
- 完美保留标题层级、表格结构、样式格式
- 支持 PDF 文档转换

**路径：** [document-organizer/](document-organizer/)

---

### 2. gaokao-search - 高考志愿搜索技能
搜索阳光高考平台，汇总目标专业对应的高校招生信息，包括学校性质、招生链接、历年录取分数等。

**核心能力：**
- 自动检索开设目标专业的所有高校
- 获取学校性质（985/211/双一流）
- 抓取过去三年招生人数与录取分数线
- 支持反爬处理和兜底抓取

**路径：** [gaokao-search/](gaokao-search/)

---

### 3. convert-markdown - 文档转换技能
基于 Microsoft MarkItDown 工具，支持多种格式文件批量转换为 Markdown。

**核心能力：**
- 支持 PDF、Word、PPT、Excel、图片、音频等格式
- 结构化保留：标题、列表、表格、链接
- OCR 文本识别和音频转录
- NPX CLI 支持，可直接通过 `npx convert-markdown` 调用

**运行环境：**
- Python 3.10+（必需）
- Node.js 14.0+（必需）
- Tesseract OCR（可选，用于 PDF OCR）
- FFmpeg（可选，用于音频转录）

**版本信息：**
- 当前版本：1.1.0
- 基于：Microsoft MarkItDown 0.1.5+

**路径：** [convert-markdown/](convert-markdown/)

---

### 4. search-kb - 知识库搜索技能
高性能全文搜索技能，支持在大量 Markdown 文档中快速检索内容。

**核心能力：**
- 支持模糊搜索和相关性排序
- 搜索结果上下文预览
- 缓存机制提升搜索速度
- 适合项目文档、培训材料检索

**路径：** [search-kb/](search-kb/)

---

### 5. web-search-multi - 多提供商网页搜索技能
多 provider 并行搜索技能，支持 Bing、Sogou、Tavily 等提供商并行搜索和结果合并。

**核心能力：**
- 多 provider 并行搜索（Bing + Sogou + Tavily）
- 轮询合并策略，智能去重
- 内存缓存（5分钟 TTL）
- OpenClaw Tool Calling 兼容

**路径：** [web-search-multi/](web-search-multi/)

---

## 🚀 快速开始

每个技能目录下都包含详细的 SKILL.md 文档，请进入对应目录查看：

```bash
# 查看技能详情
cat document-organizer/SKILL.md
cat gaokao-search/SKILL.md
cat convert-markdown/SKILL.md
cat search-kb/SKILL.md
cat web-search-multi/SKILL.md
```

## 📁 项目结构

```
skills/
├── document-organizer/      # 文档整理技能
│   ├── scripts/             # 处理脚本
│   ├── SKILL.md             # 技能文档
│   └── README.md            # 使用说明
├── gaokao-search/           # 高考志愿搜索技能
│   ├── scripts/             # Python 脚本
│   ├── references/          # 参考数据
│   └── SKILL.md             # 技能文档
├── convert-markdown/         # 文档转换技能
│   ├── bin/                 # NPX CLI 入口
│   ├── scripts/             # 转换脚本
│   ├── references/          # API 参考
│   ├── package.json         # Node.js 包配置
│   └── SKILL.md             # 技能文档
├── search-kb/               # 知识库搜索技能
│   ├── bin/                 # 可执行文件
│   ├── lib/                 # 核心库
│   └── SKILL.md             # 技能文档
├── web-search-multi/        # 网页搜索技能
│   ├── bin/                 # CLI 入口
│   ├── src/                 # 源代码
│   └── SKILL.md             # 技能文档
└── README.md                # 本文件
```

## 📝 使用说明

### convert-markdown 使用示例

```bash
# 使用 NPX CLI
npx convert-markdown convert --input document.pdf --output document.md
npx convert-markdown batch --source ./docs --target ./markdown

# 使用 Python API
python -c "from markitdown import MarkItDown; print(MarkItDown().convert('doc.pdf').text_content)"
```

### web-search-multi 使用示例

```bash
# 进入目录
cd web-search-multi

# 安装依赖
npm install

# 执行搜索
node bin/web-search-multi.js '{"query":"OpenClaw AI","count":10}'
```

## ⚠️ 注意事项

### 环境依赖
- **convert-markdown**：需要 Python 3.10+ 和 Node.js 14.0+ 运行环境
- **document-organizer**：需要安装 LibreOffice（用于旧版 Office 文档转换）
- 部分技能需要安装额外的系统依赖（如 Tesseract OCR、FFmpeg）

### 使用建议
- 使用前请阅读各技能的详细文档（SKILL.md）
- 网页搜索技能请注意请求频率限制
- OCR 和音频转录功能需要额外安装依赖
- 大文件处理可能需要较长时间
