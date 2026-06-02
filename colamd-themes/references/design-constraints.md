# ColaMD 主题设计约束规范 (DC v2.0)

## 5 大核心约束

| 编号 | 约束域 | 核心规则 | 级别 |
|------|--------|----------|------|
| **DC-1** | 字体 | 中文无衬线为主，禁西文主字体；代码等宽+CJK回退 | MUST |
| **DC-2** | 字号 | H1→H6: `2/1.5/1.25/1.125/1/0.95` 严格降序（16px基准）| MUST |
| **DC-3** | 配色 | 浅色方向；同色相轴明度梯度；禁深底深字/浅底浅字 | MUST |
| **DC-4** | 扩展背景 | 与正文同系（浅-浅/深-深），差异≤15% | MUST |
| **DC-5** | 打印 | @media print 变量与屏幕版完全一致 | MUST |

---

## DC-1: 字体约束

### DC-1.1 中文无衬线字体栈（MUST）

```css
/* 正文/标题 - 中文无衬线 */
--font-body: -apple-system, "PingFang SC", "Hiragino Sans GB",
             "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif;
```

**禁止**: 西文字体（Inter, Roboto 等）作为主字体
**禁止**: @font-face 作为 body 主字体

### DC-1.2 代码块等宽 + CJK 回退（MUST）

```css
--font-code: "SF Mono", "Menlo", "Monaco", "Consolas",
             "Liberation Mono", "Courier New",
             "PingFang SC", "Microsoft YaHei", monospace;
```

### DC-1.3 CJK 回退链（MUST）

```
[主要字体] → [macOS: PingFang SC] → [Windows: Microsoft YaHei] → [Linux] → [通用]
```

---

## DC-2: 字号层级

### DC-2.1 标准缩放倍率（MUST）

| 级别 | 倍率 | 尺寸 (16px) | 行高 | 下边距 |
|------|------|-------------|------|--------|
| H1 | 2.0 | 32px | 1.3 | 1.5em |
| H2 | 1.5 | 24px | 1.35 | 1.25em |
| H3 | 1.25 | 20px | 1.4 | 1em |
| H4 | 1.125 | 18px | 1.5 | 0.75em |
| H5 | 1.0 | 16px | 1.5 | 0.75em |
| H6 | 0.95 | 15.2px | 1.5 | 0.75em |

### DC-2.2 CSS 变量实现

```css
--font-size-root: 16px;
--font-scale-h1: 2.0;   --font-scale-h2: 1.5;   --font-scale-h3: 1.25;
--font-scale-h4: 1.125; --font-scale-h5: 1.0;    --font-scale-h6: 0.95;
```

---

## DC-3: 配色约束

### DC-3.1 浅色方向（MUST）

surface L ≥ 95%（极浅灰或纯白），贴近现代中文文档站点清爽风格。

### DC-3.2 同色相轴明度梯度（MUST）

surface / panel / panelAlt / border 必须**同色相轴**，仅明度递进：

```css
/* ✅ 正确：灰轴 */
--seed-surface:   hsl(0, 0%, 99%);
--seed-panel:     hsl(0, 0%, 96%);
--seed-panelAlt:  hsl(0, 0%, 93%);
--seed-border:    hsl(0, 0%, 88%);

/* ❌ 错误：不同色相 */
--seed-panel:  #F0F4FF; /* 蓝调 - 违反！ */
--seed-border: #FFE0E0; /* 红调 - 违反！ */
```

### DC-3.3 禁止反向组合（MUST）

| 组合 | 允许？ |
|------|--------|
| 浅底 + 深字 | ✅ 必须 |
| 深底 + 浅字 | ✅ 仅深色模式 |
| **深底 + 深字** | ❌ **禁止** |
| **浅底 + 浅字** | ❌ **禁止** |

**对比度要求**: 正文≥7:1(AAA), 次要≥4.5:1(AA), 辅助≥3:1

---

## DC-4: 扩展元素背景约束

### DC-4.1 同系原则（MUST）

扩展元素背景必须与正文表层**同系**，亮度差异 ≤15%：

| 元素 | 推荐背景 | 说明 |
|------|----------|------|
| 代码块 | `#F8F8F8` | 比surface暗2-4% |
| 行内代码 | `#F0F0F0` | 比surface暗5-8% |
| 引用块 | `#FAFAFA` | 比surface暗1-2% |
| Mermaid | panel色 | 与面板协调 |
| 表格头 | panel色 | 与面板一致 |

```css
/* ✅ 正确：浅色模式用浅灰 */
.md-code-block { background: #F8F8F8; }

/* ❌ 错误：浅色模式用深色/强彩色 */
.md-code-block { background: #1E1E1E; } /* 差异过大！ */
.mermaid        { background: #FFEBEE; } /* 不协调！ */
```

---

## DC-5: 打印同步约束

### DC-5.1 变量一致性（MUST）

@media print 内变量重声明必须与屏幕版**完全一致**：

```css
/* ✅ 正确 */
@media print {
  :root {
    --seed-surface: var(--seed-surface);
    --seed-ink: var(--seed-ink);
  }
}

/* ❌ 禁止：打印版独有配色/字体 */
@media print {
  --seed-surface: #FFFFCC; /* 黄色纸张 - 不允许！ */
  font-family: "SimSun";   /* 切换宋体 - 不允许！ */
}
```

### DC-5.2 允许/禁止操作

| 允许 ✅ | 禁止 ❌ |
|---------|---------|
| 隐藏导航栏/侧边栏 | 修改变量值 |
| 移除背景图/渐变 | 引入新配色方案 |
| `print-color-adjust: exact` | 切换字体族 |
| 调整 padding/margin | 改变布局结构 |

---

## 验证清单

生成主题后逐项检查：

- [ ] **DC-1**: 主字体为中文无衬线，含 CJK 回退；代码等宽+CJK
- [ ] **DC-2**: H1-H6 严格降序，使用标准倍率
- [ ] **DC-3**: 浅色方向；同色相轴；无反向组合；对比度达标
- [ ] **DC-4**: 扩展元素背景与正文同系，差异≤15%
- [ ] **DC-5**: @media print 无独有配色/字体声明
