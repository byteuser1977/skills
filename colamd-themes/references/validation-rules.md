# v3.0 范式验证规则参考

ColaMD Themes 使用 WCAG 2.1 对比度标准和设计约束规则验证生成的 CSS 主题。

## 目录

- [对比度规则 (CR)](#对比度规则-cr)
- [饱和度规则 (sl)](#饱和度规则-sl)
- [亮度规则 (nt)](#亮度规则-nt)
- [边界规则 (bd)](#边界规则-bd)
- [映射规则 (mp)](#映射规则-mp)
- [字体规则 (fp/fs)](#字体规则-fpfs)
- [阴影规则 (sh)](#阴影规则-sh)

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

---

## 亮度规则 (NT)

区分明暗模式，确保一致性。

### NT-01: 明暗模式一致性

- **级别**: MUST
- **检查**: 所有颜色的明暗模式判断必须一致
- **方法**: 基于 surface 的 HSL Lightness 判断：
  - Light mode: `lightness > 0.5`
  - Dark mode: `lightness <= 0.5`

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

---

## 阴影规则 (SH)

### SH-01: 避免强阴影干扰阅读

- **级别**: SHOULD_NOT
- **检查**: box-shadow 不应过大或过深

---

## 验证命令

```bash
# 验证单个主题文件
node dist/cli.ts validate themes/my-theme.css

# 验证输出示例:
# ✅ CR-01: 正文-底色对比度 8.2:1 PASS
# ⚠️ SL-03: 强调色饱和度 12% < 15% (SHOULD)
# ❌ BD-01: panel 亮度异常 (MUST)
```

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
  fix: "建议加深 ink 或调浅 surface"
}
```
