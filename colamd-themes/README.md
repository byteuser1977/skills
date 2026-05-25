# ColaMD Themes 技能

本技能提供了完整的 ColaMD 主题生成、验证和管理工作流。

## 快速开始

### 1. 安装依赖

确保已在 ColaMD-themes 项目目录中安装依赖：

```bash
cd /mnt/d/workspace/git/ColaMD-themes
npm install
npm run build
```

### 2. 基本使用

使用 wrapper 脚本运行命令：

```bash
# 从文件自动提取并生成主题
cd /mnt/d/workspace/git/skills/colamd-themes
./scripts/colamd-themes-wrapper.sh extract /path/to/source.docx -n "my-theme" -A

# 验证生成的 CSS
./scripts/colamd-themes-wrapper.sh validate themes/my-theme.css

# 列出现有主题
./scripts/colamd-themes-wrapper.sh list

# 查看可用的颜色系统
./scripts/colamd-themes-wrapper.sh color-systems
```

或者直接进入 ColaMD-themes 项目使用 npx：

```bash
cd /mnt/d/workspace/git/ColaMD-themes
npx tsx src/cli.ts extract source.pdf -n "theme" --auto-match
```

详细命令参考，请查看 [SKILL.md](./SKILL.md)。

## 支持的源格式

- **URL**：网页链接（自动解析 CSS 规则）
- **DOCX**：Word 文档（.docx）
- **PDF**：带文本层的 PDF

## 输出的主题结构

生成的主题 CSS 文件包含 6 个 SECTION：

1. **Design Tokens**：种子颜色和字体（用户可编辑）
2. **Semantic Mapping**：语义变量映射
3. **Mermaid Variables**：图表配色（20 个变量）
4. **Fine Tuning**：微调
5. **Selector Adjustments**：选择器级调整
6. **Print Styles**：打印样式

## 依赖的项目

本技能依赖于外部的 [ColaMD-themes](https://github.com/byteuser1977/ColaMD-themes) 项目。请确保：

- Node.js ≥ 18
- ColaMD-themes 项目已克隆到 `/mnt/d/workspace/git/ColaMD-themes`
- 已运行 `npm install` 和 `npm run build`

## 故障排除

- **命令找不到**：确认已在 ColaMD-themes 项目根目录运行过 `npm install`
- **编译错误**：运行 `npm run build` 重新编译
- **提取失败**：检查源文件路径是否正确，PDF 需要文本层而非扫描图像

详细故障排除请参考主技能文档 [SKILL.md](./SKILL.md)。
