# 文档整理技能 - 快速使用指南

## 🚀 一键使用

```bash
# 1. 扫描并统计（不转换）
npx skills run document-organizer --source "G:\历史文档" --dry-run

# 2. 执行批量转换
npx skills run document-organizer --source "G:\历史文档" --output "d:\知识库"

# 3. 仅处理 Word 文档
npx skills run document-organizer --source "G:\docs" --type doc,docx
```

---

## 📁 **目录结构示例**

**输入**:
```
G:\历史文档/
├── 项目A/
│   ├── 需求.doc
│   ├── 设计.doc
│   └── 会议记录.xls
└── 项目B/
    └── 报告.ppt
```

**输出**:
```
d:\知识库/
├── 项目A/
│   ├── 需求.md      (格式完美)
│   ├── 设计.md      (表格保留)
│   └── 会议记录.md   (Excel 转 Markdown 表格)
└── 项目B/
    └── 报告.md      (PPT 转 Markdown)
```

---

## 🔧 **常见参数**

| 参数 | 示例 | 说明 |
|------|------|------|
| `--source` | `--source "G:\docs"` | 源目录（必需） |
| `--output` | `--output "d:\md"` | 输出目录（默认: ./output） |
| `--type` | `--type doc,xls` | 处理的文件类型（默认: doc,xls,docx,xlsx） |
| `--soffice-path` | `--soffice-path "D:\LibreOffice\soffice.exe"` | LibreOffice 路径（自动检测） |
| `--dry-run` | `--dry-run` | 仅扫描统计，不转换 |

---

## ✅ **质量保证**

- **格式化保留**: 标题、加粗、斜体、列表
- **表格支持**: Excel 表格 → Markdown 表格
- **编码正确**: 全程 UTF-8，中文无乱码
- **错误容忍**: 单个文件失败不影响整体

---

## 📊 **性能参考**

| 规模 | 预计时间 |
|------|----------|
| 100 文件 | ~1-2 分钟 |
| 1,000 文件 | ~5-10 分钟 |
| 3,000 文件 | ~15-20 分钟 |

---

## 🆘 **故障排除**

**问题**: `LibreOffice not found`
```
解决: 安装 LibreOffice 或使用 --soffice-path 指定路径
下载: https://zh-cn.libreoffice.org/
```

**问题**: 转换失败
```
解决: 检查错误日志 (conversion.log)
常见: 源文件损坏、权限不足
```

**问题**: 输出文件乱码
```
解决: 确保系统区域设置为 UTF-8，或检查源代码文件编码
```

---

## 📚 **高级用法**

### 递归子目录（默认开启）

```bash
# 自动扫描所有子目录
npx skills run document-organizer --source "G:\docs" --recursive
```

### 保持目录结构（默认开启）

```bash
# 输出时保持与源目录相同的子目录结构
npx skills run document-organizer --keep-structure
```

### 自定义临时目录

```bash
# 指定临时文件存放位置（默认: ./temp_batch）
npx skills run document-organizer --temp-dir "D:\temp"
```

---

## 🔄 **完整工作流示例**

```bash
# Step 1: 扫描统计
npx skills run document-organizer --source "G:\VSS_SINOCHEM" --dry-run
# 输出: 将处理 2990 文件 (982 .doc, 2008 .xls)

# Step 2: 实际转换（约 15 分钟）
npx skills run document-organizer --source "G:\VSS_SINOCHEM" --output "d:\knowledge\VSS_SINOCHEM"

# Step 3: 重建知识库索引
node d:\workspace\clawd\knowledge\build_index.js

# Step 4: 验证搜索
search-kb "关键词"
```

---

**版本**: 1.0  
**更新**: 2026-03-11  
**适用**: OpenClaw Skills Framework
