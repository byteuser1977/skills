# 文档整理技能 - 快速使用指南

> 一句话: `npx skills run document-organizer --source 源目录 --output 输出目录`

---

## 🚀 5 分钟快速上手

### 1. 安装依赖

```bash
# 1) 安装 LibreOffice (仅旧版格式需要)
#    下载: https://zh-cn.libreoffice.org/

# 2) 安装 Python 包（包含 PDF 支持）
pip install 'markitdown[docx,xlsx,pdf]'
```

### 2. 基本使用

```bash
# 最简单: 转换整个目录
npx skills run document-organizer --source "G:\历史文档"

# 指定输出目录
npx skills run document-organizer --source "G:\docs" --output "D:\知识库"

# 查看帮助
npx skills run document-organizer --help
```

---

## 📋 常用命令速查

| 场景 | 命令 |
|------|------|
| **转换所有格式** | `npx skills run document-organizer --source "G:\docs" --output "D:\md"` |
| **仅 Word 文档** | `npx skills run document-organizer --source "G:\docs" --type doc,docx` |
| **仅 Excel 表格** | `npx skills run document-organizer --source "G:\docs" --type xls,xlsx` |
| **仅 PDF** | `npx skills run document-organizer --source "G:\pdfs" --type pdf` |
| **预览（不转换）** | `npx skills run document-organizer --source "G:\docs" --dry-run` |
| **详细日志** | `npx skills run document-organizer --source "G:\docs" --verbose` |
| **指定 LibreOffice** | `npx skills run document-organizer --source "G:\docs" --soffice-path "D:\LibreOffice\soffice.exe"` |

---

## 🎯 典型使用场景

### 场景 1: 历史文档批量数字化

**目标**: 将 2,990 个旧版 Office 文件（`.doc` + `.xls`）转为 Markdown

```bash
npx skills run document-organizer \
  --source "G:\VSS_SINOCHEM" \
  --output "d:\workspace\clawd\knowledge\VSS_SINOCHEM" \
  --type doc,xls \
  --log-file "d:\workspace\clawd\state\vss_sinochem.log" \
  --verbose
```

**预计**: ~15 分钟完成

---

### 场景 2: PDF 库转换

**目标**: 将 PDF 文档库转为可搜索的 Markdown

```bash
npx skills run document-organizer \
  --source "G:\PDF_Library" \
  --output "D:\PDF_Markdown" \
  --type pdf \
  --temp-dir "D:\NVMe_SSD\temp"
```

**注意**: 扫描版 PDF 需要 OCR，安装:
```bash
pip install 'markitdown[pdf]'
# 并安装 Tesseract OCR: https://github.com/tesseract-ocr/tesseract
```

---

### 场景 3: 混合格式统一处理

**目标**: 项目中既有旧版又有新版 Office 文件，统一输出

```bash
# 默认已包含所有格式
npx skills run document-organizer \
  --source "G:\ProjectX" \
  --output "D:\ProjectX_MD"
```

**自动匹配**:
- `.doc` 和 `.docx` 都会处理
- `.xls` 和 `.xlsx` 都会处理
- `.ppt` 和 `.pptx` 都会处理

---

### 场景 4: 快速测试（前 10 个文件）

```bash
# 1. Dry Run 查看统计
npx skills run document-organizer --source "G:\big_docs" --dry-run

# 2. 创建测试子集
mkdir test_samples
xcopy "G:\big_docs\00_公告区" "test_samples\" /s /y
# 只复制少量文件

# 3. 测试转换
npx skills run document-organizer --source "test_samples" --output "test_output"
```

---

### 场景 5: 增量更新

**目标**: 只转换新添加的文件（避免重复转换）

```bash
# 1. 记录已转换的文件清单（手动或脚本）
# 2. 使用 exclude 参数跳过已转换目录

# 示例: 跳过已处理过的 "2023" 和 "2024" 目录
npx skills run document-organizer \
  --source "G:\annual_reports" \
  --exclude "2023/*,2024/*"
```

**高级**: 编写脚本检查文件修改时间，只转换最近修改的文件（见 `EXAMPLES.md`）

---

## ⚙️ 参数详解

### 必需参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `--source` | `str` | **源目录路径**（必需） | `--source "G:\docs"` |

### 可选参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--output` | `str` | `./output` | 输出目录（不存在则创建） |
| `--type` | `str` | `doc,xls,docx,xlsx,ppt,pptx,pdf` | 处理的文件类型，逗号分隔 |
| `--soffice-path` | `str` | 自动检测 | LibreOffice 路径（旧版格式需要） |
| `--temp-dir` | `str` | `./temp_batch` | 临时文件目录（自动清理） |
| `--log-file` | `str` | `conversion.log` | 错误日志文件路径 |
| `--dry-run` | `bool` | `false` | 仅扫描统计，不转换 |
| `--verbose` | `bool` | `false` | 显示详细日志 |

---

## 📁 目录结构保持

技能会**自动保持源目录结构**：

```
源目录:
G:\docs\
├── 项目A\
│   ├── 需求.docx
│   └── 设计.xlsx
└── 项目B\
    └── 报告.ppt

输出目录 (自动创建):
D:\md\
├── 项目A\
│   ├── 需求.md
│   └── 设计.md
└── 项目B\
    └── 报告.md
```

---

## 🐛 常见问题快速解决

### 问题 1: "LibreOffice not found"

```bash
# 解决方案 1: 安装 LibreOffice
# https://zh-cn.libreoffice.org/

# 解决方案 2: 指定路径
npx skills run document-organizer \
  --source "docs" \
  --soffice-path "D:\Custom\LibreOffice\soffice.exe"
```

---

### 问题 2: "ModuleNotFoundError: markitdown"

```bash
# 安装依赖
pip install 'markitdown[docx,xlsx,pdf]'

# 如果使用虚拟环境，确保已激活
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

---

### 问题 3: 转换慢

**优化方案**:
1. 临时目录放 SSD
2. 排除过大的文件（单独处理）
3. 考虑分批处理（分目录多次运行）

```bash
npx skills run document-organizer \
  --source "G:\docs" \
  --temp-dir "D:\NVMe_SSD\temp" \
  --log-file "D:\logs\conversion.log"
```

---

### 问题 4: 个别文件失败

**查看错误日志**:
```bash
type conversion.log
# 或
notepad conversion.log
```

**跳过特定文件**:
```bash
# 手动移动失败文件到单独目录
move bad_file.doc failed_files\
# 重新运行转换
```

---

## 📊 性能参考

### 典型吞吐量（i5 CPU, SSD）

| 格式 | 速度 | 1,000 文件预估 |
|------|------|---------------|
| `.doc` | ~35 个/秒 | ~30 秒 |
| `.xls` | ~20 个/秒 | ~50 秒 |
| `.docx` | ~50 个/秒 | ~20 秒 |
| `.xlsx` | ~15 个/秒 | ~70 秒 |
| `.pdf` | ~4 个/秒 | ~4 分钟 |

**3,000 文件混合**: **~10-15 分钟**

---

## 🔍 验证转换质量

转换完成后，快速验证：

```bash
# 1. 检查文件数量
dir "D:\output\**\*.md" /s /b | find /c ".md"

# 2. 抽查文件内容
notepad "D:\output\项目A\需求.md"

# 3. 搜索关键词测试
# （如果配置了 search-kb）
npx skills run search-kb --query "关键词"
```

---

## 📚 更多资源

| 文档 | 说明 |
|------|------|
| `SKILL.md` | 完整技能规范（架构、依赖、API） |
| `README.md` | 用户指南（快速开始、示例）|
| `references/API_REFERENCE.md` | 函数 API 详细说明 |
| `references/FORMATS.md` | 所有格式的处理细节 |
| `references/CONFIGURATION.md` | 高级配置选项 |
| `references/TROUBLESHOOTING.md` | 故障排除大全 |
| `references/PERFORMANCE.md` | 性能调优指南 |
| `references/EXAMPLES.md` | 大量实用代码示例 |

---

## 💡 小贴士

1. **首次使用** → 先用 `--dry-run` 预览
2. **大量文件** → 确保临时目录在 SSD
3. **旧版 Office** → 确保 LibreOffice 已安装
4. **PDF 转换** → 需要安装 `markitdown[pdf]`
5. **日志在哪** → 默认当前目录 `conversion.log`
6. **保持目录** → 自动保持，无需配置
7. **错误处理** → 自动跳过失败文件，继续其他
8. **支持格式** → `doc, xls, docx, xlsx, ppt, pptx, pdf`

---

## 🆘 需要帮助？

1. **查看文档**: 本目录所有 `.md` 文件
2. **运行诊断**:
   ```bash
   npx skills run document-organizer --source "docs" --dry-run --verbose
   ```
3. **查看日志**: `conversion.log`
4. **社区支持**: OpenClaw Discord / GitHub Issues

---

**快速命令卡**:

```bash
# 常用 3 命令
npx skills run document-organizer --source "源目录" --output "输出目录"
npx skills run document-organizer --source "源目录" --dry-run    # 预览
npx skills run document-organizer --source "源目录" --verbose     # 详细

# 帮助
npx skills run document-organizer --help
```

---

**祝使用愉快！** 🚀
