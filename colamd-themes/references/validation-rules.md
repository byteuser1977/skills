# v3.0 范式验证规则参考

基于 WCAG 2.1 对比度标准和设计约束 (DC v2.0) 验证 CSS 主题。

**设计约束完整规范**: [design-constraints.md](./design-constraints.md)

## 规则体系

| 类别 | 编号 | 核心检查 |
|------|------|----------|
| **对比度** | CR-01~06 | 文字/背景对比度达标 |
| **饱和度** | SL-01~04 | 底色低饱和、强调色高饱和 |
| **亮度** | NT-01~02 | 明暗模式一致、过渡平滑 |
| **边界** | BD-01~03 | 层次顺序正确、边框可见 |
| **映射** | MP-01~03 | 使用 var() 变量 |
| **字体** | FP-01, FS-01~02 | 字体栈完整、字号合理 |
| **字体审计** | FA-01~05 | 字体来源可追溯、一致性 |
| **配色审计** | CA-01~04 | 配色和谐、无障碍 |
| **背景前景** | BF-01~06 | 背景前景配对矩阵 |
| **图案检测** | PT-01~04 | 渐变/阴影/边框不干扰阅读 |
| **阴影** | SH-01~02 | 阴影效果适度 |
| **设计约束** | DC-1~5 | ⭐ 5大核心约束 |

---

## 核心规则速查

### 对比度 (CR)

| 规则 | 级别 | 要求 |
|------|------|------|
| CR-01 | MUST | 正文-底色 ≥ 7:1 (AAA) |
| CR-02 | MUST | 次要文字 ≥ 4.5:1 (AA) |
| CR-03 | SHOULD | 辅助文字 ≥ 3:1 |
| CR-04 | MUST | 强调色 ≥ 4.5:1 |
| CR-05 | MUST | 链接 ≥ 4.5:1 + 可辨识 |
| CR-06 | MUST | 代码块 ≥ 7:1 |

### 饱和度 (SL)

| 规则 | 级别 | 要求 |
|------|------|------|
| SL-01 | MUST | 底色饱和度 ≤ 5% |
| SL-02 | MUST_NOT | 面板饱和度 ≤ 10% |
| SL-03 | SHOULD | 强调色 ≥ 15% |
| SL-04 | SHOULD | 主辅色相差异 ≥ 30° |

### 字体 (FP/FS)

| 规则 | 级别 | 要求 |
|------|------|------|
| FP-01 | MUST | 含 CJK 回退 + 通用字体族结尾 |
| FS-01 | SHOULD | H1: 2.0-2.5, H6: 0.85-1.0 |
| FS-02 | SHOULD | 正文400, 标题600-700 |

### 字体审计 (FA)

| 规则 | 级别 | 要求 |
|------|------|------|
| FA-01 | MUST | 字体来源可追溯 |
| FA-02 | SHOULD | Web字体加载有效 |
| FA-03 | MUST | 回退链≥4级 |
| FA-04 | MUST | **所有选择器字体统一** ⭐ |
| FA-05 | SHOULD | 字体文件可用 |

### 背景前景 (BF)

| 规则 | 级别 | 要求 |
|------|------|------|
| BF-01 | MUST | 背景6类：surface/panel/panelAlt/code/quote/accent |
| BF-02 | MUST | 前景8类：ink/inkMuted/inkDim/link/code/border/divider |
| BF-03 | MUST | **配对矩阵对比度达标** ⭐ |
| BF-04 | MUST | 图案背景+20%对比度 |
| BF-05 | SHOULD | 特殊场景覆盖(深色/选中/hover/disabled) |
| BF-06 | MUST | Mermaid节点文字≥4.5:1 |

### 图案检测 (PT)

| 规则 | 级别 | 要求 |
|------|------|------|
| PT-01 | SHOULD | 渐变不干扰阅读方向 |
| PT-02 | MUST | 背景图有纯色fallback |
| PT-03 | SHOULD | 阴影不过重 |
| PT-04 | SHOULD | 边框不遮挡内容 |

---

## 设计约束规范 (DC) ⭐

详见 [design-constraints.md](./design-constraints.md)，5 大核心约束：

| 编号 | 约束域 | 核心规则 |
|------|--------|----------|
| **DC-1** | 字体 | 中文无衬线为主，禁西文主字体；代码等宽+CJK回退 |
| **DC-2** | 字号 | H1→H6: `2/1.5/1.25/1.125/1/0.95` 严格降序 |
| **DC-3** | 配色 | 浅色方向；同色相轴明度梯度；禁深底深字 |
| **DC-4** | 扩展背景 | 与正文同系，差异≤15% |
| **DC-5** | 打印 | @media print 与屏幕版完全一致 |

---

## 验证命令

```bash
# 基础验证
colamd-themes validate theme.css

# 完整审计
colamd-themes validate theme.css --full-audit
colamd-themes validate theme.css --report report.json

# 专项检查
colamd-themes validate theme.css --check fonts
colamd-themes validate theme.css --check contrast
colamd-themes validate theme.css --check design-constraints
colamd-themes validate theme.css --selector ".md-diagram-panel"
```

---

## 问题级别

| 级别 | 处理方式 |
|------|----------|
| MUST / MUST_NOT | 阻止生成，必须修复 |
| SHOULD / SHOULD_NOT | 警告，不阻止 |

## 自动修复示例

```json
{
  "ruleId": "FA-04",
  "level": "MUST",
  "message": "Mermaid .node .label 字体栈不完整",
  "fix": "统一为: \"PingFang SC\", \"Microsoft YaHei\", sans-serif"
}
```
