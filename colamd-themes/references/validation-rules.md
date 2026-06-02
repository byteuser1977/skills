# v3.0 范式验证规则参考

ColaMD Themes 使用 WCAG 2.1 对比度标准和设计约束规则验证生成的 CSS 主题。

## 目录

- [对比度规则 (CR)](#对比度规则-cr)
- [饱和度规则 (SL)](#饱和度规则-sl)
- [亮度规则 (NT)](#亮度规则-nt)
- [边界规则 (BD)](#边界规则-bd)
- [映射规则 (MP)](#映射规则-mp)
- [字体规则 (FP/FS)](#字体规则-fpfs)
- [字体提取审计 (FA)](#字体提取审计-fa)
- [配色合理性审计 (CA)](#配色合理性审计-ca)
- [背景前景识别规则 (BF)](#背景前景识别规则-bf)
- [图案检测规则 (PT)](#图案检测规则-pt)
- [阴影规则 (SH)](#阴影规则-sh)

---

## 对比度规则 (CR)

基于 WCAG 2.1 相对亮度计算，确保文字可读性。

### CR-01: 正文-底色对比度 ≥ 7:1 (WCAG AAA)

- **级别**: MUST
- **检查**: `contrastRatio(ink, surface) >= 7.0`
- **修复建议**: 加深 ink 或调浅 surface

### CR-02: 次要文字-底色对比度 ≥ 4.5:1 (WCAG AA)

- **级别**: MUST
- **检查**: `contrastRatio(inkMuted, surface) >= 4.5`

### CR-03: 辅助文字-底色对比度 ≥ 3:1

- **级别**: SHOULD
- **检查**: `contrastRatio(inkDim, surface) >= 3.0`

### CR-04: 点缀色-底色对比度 ≥ 4.5:1

- **级别**: MUST
- **检查**: `contrastRatio(accent, surface) >= 4.5`

### CR-05: 链接文字-底色对比度 ≥ 4.5:1 + 可辨识性

- **级别**: MUST
- **检查**:
  - `contrastRatio(linkColor, surface) >= 4.5`
  - 链接颜色与正文颜色差异 ≥ 3:1（确保可区分）

### CR-06: 代码块背景-代码文字对比度 ≥ 7:1

- **级别**: MUST
- **检查**: `contrastRatio(codeText, codeBackground) >= 7.0`

---

## 饱和度规则 (SL)

控制背景色的色彩纯度，避免页面偏色。

### SL-01: 底色饱和度 ≤ 5%

- **级别**: MUST
- **检查**: `hslSaturation(surface) <= 0.05`
- **原因**: 高饱和度底色会导致视觉疲劳

### SL-02: 面板饱和度 ≤ 10%

- **级别**: MUST_NOT
- **检查**: `hslSaturation(panel) <= 0.10` 且 `hslSaturation(panelAlt) <= 0.10`

### SL-03: 强调色饱和度 ≥ 15%

- **级别**: SHOULD
- **检查**: `hslSaturation(accent) >= 0.15`
- **原因**: 确保强调色有足够的视觉辨识度

### SL-04: 配色组合和谐度检查

- **级别**: SHOULD
- **检查**:
  - 主色与辅助色色相差异 ≥ 30°（避免过于相近）
  - 整体配色不超过 5 个主色调（避免杂乱）

---

## 亮度规则 (NT)

区分明暗模式，确保一致性。

### NT-01: 明暗模式一致性

- **级别**: MUST
- **检查**: 所有颜色的明暗模式判断必须一致
- **方法**: 基于 surface 的 HSL Lightness 判断：
  - Light mode: `lightness > 0.5`
  - Dark mode: `lightness <= 0.5`

### NT-02: 明暗过渡平滑性

- **级别**: SHOULD
- **检查**:
  - surface → panel → panelAlt 的亮度变化均匀（每级 ≤ 15%）
  - 避免"跳跃式"亮度变化导致视觉断层

---

## 边界规则 (BD)

确保颜色之间的层次关系正确。

### BD-01: 层次顺序

- **级别**: MUST
- **检查**:
  ```
  surface brightness > panel brightness > panelAlt brightness (light mode)
  surface brightness < panel brightness < panelAlt brightness (dark mode)
  ```

### BD-02: 边框可见性

- **级别**: SHOULD
- **检查**: border 与 panel 的对比度 ≥ 1.5:1

### BD-03: 分隔线与背景区分度

- **级别**: MUST
- **检查**: divider/horizontal-rule 与相邻背景的对比度 ≥ 2:1

---

## 映射规则 (MP)

确保 CSS 变量使用正确的引用方式。

### MP-01: 必须使用 var() 引用种子变量

- **级别**: MUST
- **禁止**: 选择器中出现裸 hex 颜色值
- **允许**: `var(--seed-accent)`, `var(--bg-color)` 等

### MP-02: 字体大小必须使用变量

- **级别**: MUST
- **禁止**: 裸像素/rem 值
- **允许**: `var(--font-size-root)`, `var(--font-scale-h1)` 等

### MP-03: 选择器覆盖完整性

- **级别**: SHOULD
- **检查**: 关键选择器是否完整覆盖：
  - 正文容器 (.md-content)
  - 标题 (h1-h6)
  - 段落 (p)
  - 列表 (ul, ol, li)
  - 代码块 (pre, code)
  - 引用块 (blockquote)
  - 表格 (table, th, td)
  - Mermaid 图表 (.md-diagram-panel)
  - 数学公式 (.katex)

---

## 字体规则 (FP/FS)

### FP-01: 字体栈完整性

- **级别**: MUST
- **要求**:
  - 包含主要字体族
  - 包含 CJK 回退字体（中文：`"PingFang SC"`, `"Microsoft YaHei"` 等）
  - 以通用字体族结尾（`sans-serif`, `serif`, `monospace`）

**示例**:
```css
--font-body: "Inter", "PingFang SC", "Microsoft YaHei", sans-serif;
--font-code: "JetBrains Mono", "Fira Code", "Consolas", monospace;
```

### FS-01: 字号倍率合理性

- **级别**: SHOULD
- **检查**: H1-H6 的 font-scale 在合理范围内（H1: 2.0-2.5, H6: 0.85-1.0）

### FS-02: 字重层级清晰

- **级别**: SHOULD
- **检查**:
  - 正文: 400 (normal)
  - 标题: 600-700 (semi-bold/bold)
  - 强调: 700 (bold)
  - 代码: 400-500

---

## 字体提取审计 (FA)

验证从源文件提取的字体信息是否完整、准确。

### FA-01: 字体来源可追溯

- **级别**: MUST
- **检查**:
  - URL 提取：CSS 中 @font-face 或 font-family 声明应与源网页一致
  - DOCX 提取：字体名称应匹配文档中使用的字体
  - PDF 提取：字体名称应从 PDF 字体字典中提取

**审计命令**:
```bash
# 提取时启用详细日志
colamd-themes from-url "https://example.com" --name "audit-theme" --verbose

# 查看提取的字体信息
colamd-themes validate themes/audit-theme.css --detail fonts
```

### FA-02: Web 字体加载验证

- **级别**: SHOULD
- **检查**:
  - 如果源使用 Google Fonts / CDN 字体，主题应包含对应 @font-face 声明或链接
  - 自定义字体应有有效的 src 指向（本地文件或 CDN）

### FA-03: 字体回退链完整性

- **级别**: MUST
- **要求**:
  - 主要字体 → 操作系统默认字体 → CJK 字体 → 通用字体族
  - 至少 4 级回退

**正例**:
```css
font-family: "LXGW WenKai", "Noto Serif SC", "Source Han Serif SC",
             "Songti SC", Georgia, "Times New Roman", serif;
```

**反例（不完整）**:
```css
font-family: "LXGW WenKai", serif;  /* 缺少中间回退 */
```

### FA-04: 各选择器字体一致性

- **级别**: MUST
- **检查**: CSS 中所有 font-family 声明应使用统一的字体栈
- **常见问题点**:
  - Mermaid 图表标签字体与正文不一致
  - 代码块字体缺少等宽字体声明
  - 引用块使用不同字体栈

### FA-05: 字体文件可用性

- **级别**: SHOULD
- **检查**:
  - 本地字体文件存在且可访问
  - 远程字体 URL 可访问（非 404）
  - 字体格式兼容（woff2 > woff > ttf）

---

## 配色合理性审计 (CA)

审计生成的配色方案是否符合设计美学和可用性原则。

### CA-01: 色彩数量控制

- **级别**: SHOULD
- **检查**:
  - 种子颜色数量 = 11（符合 SeedPalette 规范）
  - 衍生颜色不超过 20 个
  - 总色彩数 ≤ 35（避免过度复杂）

### CA-02: 色彩心理学一致性

- **级别**: SHOULD
- **检查**:
  - 商务/正式场景：使用低饱和度、中性色调
  - 创意/活泼场景：可使用高饱和度强调色
  - 学术/技术场景：偏好冷色调（蓝、绿、灰）

### CA-03: 色彩文化适应性

- **级别**: SHOULD
- **检查**:
  - 避免在某些文化中有负面含义的颜色组合
  - 考虑目标受众的文化背景

### CA-04: 色彩无障碍性

- **级别**: MUST
- **检查**:
  - 不仅依赖颜色传达信息（配合图标/文字）
  - 色盲友好：关键信息不仅用红绿区分

---

## 背景前景识别规则 (BF)

核心审计规则：确保背景色与前景元素（文字、图案）的有效识别。

### BF-01: 背景分类识别

- **级别**: MUST
- **背景类型**:

| 类型 | 变量 | 用途 |
|------|------|------|
| **主背景** | `--seed-surface` | 页面整体底色 |
| **面板背景** | `--seed-panel` | 卡片、侧边栏 |
| **交替面板** | `--seed-panelAlt` | 斑马纹表格行 |
| **代码背景** | 自定义 | 代码块底色 |
| **引用背景** | 自定义 | 引用块底色 |
| **强调背景** | 基于 accent | 高亮区域 |

### BF-02: 前景元素清单

- **级别**: MUST
- **前景元素**:

| 元素 | 变量 | 对比目标 |
|------|------|----------|
| **正文文字** | `--seed-ink` | surface |
| **次要文字** | `--seed-inkMuted` | surface |
| **辅助文字** | `--seed-inkDim` | surface |
| **标题文字** | 继承 ink | surface |
| **链接文字** | link color | surface |
| **代码文字** | code text | code background |
| **边框线条** | `--seed-border` | panel/surface |
| **分割线** | divider | 相邻背景 |

### BF-03: 背景前景配对矩阵

- **级别**: MUST
- **审计方法**: 对每个背景-前景配对进行对比度检查

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

### BF-04: 图案/纹理背景处理

- **级别**: MUST
- **检查**:
  - 如果背景有图案/纹理（渐变、噪点、图片），前景对比度需额外 +20%
  - 图案不应干扰文字阅读（透明度 ≤ 15% 或图案密度低）

### BF-05: 特殊场景识别

- **级别**: SHOULD
- **场景列表**:

| 场景 | 审计要点 |
|------|----------|
| **深色模式** | 所有对比度自动提升 1.5 级 |
| **高亮文本** | highlight 背景与选中文字对比度 |
| **选中状态** | selection 背景与前景可读 |
| **悬停状态** | hover 时对比度不降低 |
| **焦点环** | focus ring 与相邻元素可区分 |
| **禁用状态** | disabled 文字仍可辨认（≥2:1） |

### BF-06: Mermaid 图表配色审计

- **级别**: MUST
- **检查**:
  - 节点背景 vs 节点文字 ≥ 4.5:1
  - 连线颜色与背景可区分
  - 图例文字可读

---

## 图案检测规则 (PT)

检测并审计 CSS 中可能影响阅读的图案/装饰元素。

### PT-01: 渐变背景检测

- **级别**: SHOULD
- **检查**:
  - linear-gradient / radial-gradient 使用位置
  - 渐变方向是否合理（避免干扰阅读方向）
  - 渐变起止颜色对比度

### PT-02: 背景图片/纹理

- **级别**: MUST
- **检查**:
  - background-image 是否存在
  - 如存在，必须有 fallback 纯色背景
  - 图片透明度/混合模式不影响文字可读性

### PT-03: 阴影效果审计

- **级别**: SHOULD
- **检查**:
  - box-shadow 不产生"脏"视觉效果
  - text-shadow 不降低文字清晰度
  - 阴影颜色与背景协调

### PT-04: 边框装饰

- **级别**: SHOULD
- **检查**:
  - border-style 不为 none 时边框可见
  - outline/focus-ring 不遮挡内容
  - 圆角 border-radius 与设计风格一致

---

## 阴影规则 (SH)

### SH-01: 避免强阴影干扰阅读

- **级别**: SHOULD_NOT
- **检查**: box-shadow 不应过大或过深

### SH-02: 阴影颜色一致性

- **级别**: SHOULD
- **检查**: 阴影颜色应基于 seed 颜色变量，而非硬编码

---

## 审计工作流

### 完整审计流程

```bash
# 步骤1：提取主题（启用详细日志）
colamd-themes extract <source> --name "audit-theme" --verbose -o themes/

# 步骤2：基础范式验证
colamd-themes validate themes/audit-theme.css

# 步骤3：详细审计（字体+配色）
colamd-themes validate themes/audit-theme.css --full-audit

# 步骤4：生成审计报告
colamd-themes validate themes/audit-theme.css --report audit-report.json
```

### 审计报告输出示例

```json
{
  "theme": "audit-theme",
  "timestamp": "2026-01-15T10:30:00Z",
  "summary": {
    "totalChecks": 45,
    "passed": 42,
    "warnings": 2,
    "errors": 1,
    "score": 93
  },
  "sections": {
    "contrast": { "passed": 6, "warnings": 1, "errors": 0 },
    "fonts": { "passed": 5, "warnings": 0, "errors": 1 },
    "colors": { "passed": 8, "warnings": 1, "errors": 0 },
    "patterns": { "passed": 4, "warnings": 0, "errors": 0 }
  },
  "issues": [
    {
      "ruleId": "FA-04",
      "level": "MUST",
      "message": "Mermaid .node .label 字体栈不完整，缺少 Source Han Serif SC",
      "location": "line 145",
      "fix": "添加缺失的字体到 font-family 声明"
    }
  ]
}
```

### 快速诊断命令

```bash
# 仅检查字体问题
colamd-themes validate theme.css --check fonts

# 仅检查对比度
colamd-themes validate theme.css --check contrast

# 检查特定选择器
colamd-themes validate theme.css --selector ".md-diagram-panel"

# 导出可视化报告
colamd-themes validate theme.html --visual-report
```

---

## 验证问题级别说明

| 级别 | 含义 | 处理方式 |
|------|------|----------|
| MUST | 必须满足 | 阻止生成，必须修复 |
| MUST_NOT | 必须避免 | 阻止生成，必须修复 |
| SHOULD | 建议满足 | 警告但不阻止 |
| SHOULD_NOT | 建议避免 | 警告但不阻止 |

## 自动修复建议

验证引擎会在检测到问题时提供 `fix` 建议：

```typescript
{
  ruleId: "CR-01",
  level: "MUST",
  message: "正文-底色对比度 5.5:1 < 7:1 (WCAG AAA)",
  fix: "建议加深 ink (#333→#111) 或调浅 surface (#fafafa→#ffffff)"
}

{
  ruleId: "FA-04",
  level: "MUST",
  message: "Mermaid 图表字体栈不完整",
  fix: "统一为: \"LXGW WenKai\", \"Noto Serif SC\", \"Source Han Serif SC\", \"Songti SC\", Georgia, serif"
}

{
  ruleId: "BF-03",
  level: "MUST",
  message: "代码块背景-前景对比度不足 5:1",
  fix: "调整 --code-background 或 --code-text 颜色值"
}
```
