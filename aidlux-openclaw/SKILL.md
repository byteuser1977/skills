---
name: aidlux-openclaw
description: AidLux 环境下 OpenClaw Gateway 的自启动配置与环境检测
version: 1.0.0
icon: 🛠️
---

# aidlux-openclaw

AidLux 环境下 OpenClaw Gateway 的自启动配置与环境检测工具。

## 基本信息

| 字段 | 值 |
|------|-----|
| **名称** | `aidlux-openclaw` |
| **描述** | OpenClaw 自启动服务安装与环境检测 |
| **作者** | byteuser |
| **版本** | 1.0.0 |
| **许可证** | MIT |
| **入口文件** | `./index.cjs` |

## 提供的命令

| 命令 | 说明 |
|------|------|
| `check_status` | 检查 OpenClaw Gateway 运行状态 |
| `enable_autostart` | 配置自启动服务 |
| `view_logs` | 查看日志 |
| `diagnose` | 运行诊断 |
| `full_setup` | 一键完成所有配置 |

## 使用方法

### 命令行调用

```bash
node index.cjs check_status
node index.cjs enable_autostart --method=both
node index.cjs view_logs --tail 100
node index.cjs diagnose
node index.cjs full_setup
```

### OpenClaw 会话调用

```javascript
await tool('aidlux-openclaw', { command: 'check_status' });
await tool('aidlux-openclaw', { command: 'enable_autostart', method: 'both' });
await tool('aidlux-openclaw', { command: 'view_logs', tail: 50 });
```

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2026-03-24 | 初始版本 |

**最后更新：** 2026-03-24
