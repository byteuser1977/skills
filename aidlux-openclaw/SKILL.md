# aidlux-openclaw Skill

**AidLux 环境下 OpenClaw 相关的工具**

---

## 📋 基本信息

| 字段 | 值 |
|------|-----|
| **名称** | `aidlux-openclaw` |
| **描述** | AidLux环境下openclaw相关的工具：1、自启动服务安装 ；2、系统环境检测|
| **作者** | byteuser |
| **版本** | 1.0.0 |
| **许可证** | MIT |
| **入口文件** | `./index.cjs` |

---

## 🏷️ 标签

- `aidlux` - AidLux 系统集成
- `openclaw` - OpenClaw Gateway
- `gateway` - 网关服务
- `service` - 服务管理
- `daemon` - 守护进程
- `startup` - 启动配置
- `android` - Android 平台
- `termux` - Termux 环境

---

## 🔧 提供的命令

### ✅ 已实现的命令（2 个）

| 命令 | 说明 |
|------|------|
| `install` | 安装自启动（生成 3.sh 和 rc?.d 符号链接） |
| `check_env` | 检查运行环境（which 检测路径，结果存 memory） |

## 🎯 设计原则

- **极简架构：** 仅 2 个命令，去除复杂的路径检测器
- **实用优先：** 使用 `which` 直接检测命令路径
- **结果持久化：** 环境检测结果保存到 `memory/` 目录
- **易于理解：** 代码简洁，逻辑清晰

---

## 🎯 使用方法

### 命令行直接调用

```bash
# 检查状态
node index.cjs check_status

# 配置自启动
node index.cjs enable_autostart --method=both
node index.cjs enable_autostart --method=aidlux
node index.cjs enable_autostart --method=sysv

# 查看日志
node index.cjs view_logs --tail 100

# 诊断
node index.cjs diagnose

# 完整设置
node index.cjs full_setup

# 帮助
node index.cjs --help
```

### 通过 OpenClaw 会话调用

```javascript
await tool('aidlux-openclaw', { command: 'check_status' });
await tool('aidlux-openclaw', { command: 'enable_autostart', method: 'both' });
await tool('aidlux-openclaw', { command: 'view_logs', tail: 50 });
```

---

## 🔍 功能详解

### 1. check_status

**作用：** 全面检查 OpenClaw Gateway 在 AidLux 中的状态

**输出内容：**
- 环境信息（系统类型、Node.js 版本、OpenClaw 版本）
- 服务运行状态（是否运行、PID、命令）
- 自启动配置（SysV init 和 AidLux 3.sh）
- 所有关键文件路径（PID、日志、脚本、配置）

**示例输出：**
```
=== OpenClaw Gateway 状态检查 ===

--- 环境信息 ---
系统类型: Unknown
Node.js: v24.14.0
OpenClaw: 0.1.7-fix.1

✅ 服务运行中 (PID: 12213)

--- 自启动配置 ---
✅ SysV init: 已启用
   /etc/rc2.d/S99openclaw-gateway -> ../init.d/openclaw-gateway
   /etc/rc3.d/S99openclaw-gateway -> ../init.d/openclaw-gateway
   /etc/rc4.d/S99openclaw-gateway -> ../init.d/openclaw-gateway
   /etc/rc5.d/S99openclaw-gateway -> ../init.d/openclaw-gateway
✅ AidLux (3.sh): 存在且可执行

--- 关键文件 ---
✅ PID 文件: /home/aidlux/.openclaw/gateway.pid
✅ 日志文件: /home/aidlux/.openclaw/gateway.log
✅ Init 脚本: /etc/init.d/openclaw-gateway
✅ AidLux 脚本: /etc/aidlux/3.sh
✅ Entry 文件: /home/aidlux/.nvm/versions/node/v24.14.0/lib/node_modules/openclaw-cn-termux/dist/entry.js
```

---

### 2. enable_autostart

**作用：** 配置 OpenClaw Gateway 的自启动方式

**选项：**
- `--method both` - 同时配置 SysV 和 AidLux（默认）
- `--method sysv` - 仅配置 SysV init
- `--method aidlux` - 仅配置 AidLux 3.sh

**执行操作：**
1. 备份现有 init 脚本（如果存在）
2. 创建 rc2.d/rc3.d/rc4.d/rc5.d 符号链接
3. 创建/更新 `/etc/aidlux/3.sh`（v3.0 极简版）
4. 设置正确的权限和所有权

**示例：**
```bash
node index.cjs enable_autostart --method=both
```

**输出：**
```
=== 配置自启动 ===

检测到的环境: Unknown
Node.js: v24.14.0

📦 已备份: /home/aidlux/clawd/backup/openclaw-gateway
--- 配置 SysV init ---
✅ 创建: /etc/rc2.d/S99openclaw-gateway
✅ 创建: /etc/rc3.d/S99openclaw-gateway
✅ 创建: /etc/rc4.d/S99openclaw-gateway
✅ 创建: /etc/rc5.d/S99openclaw-gateway

--- 配置 AidLux (3.sh) ---
✅ 创建/更新: /etc/aidlux/3.sh

✅ 自启动配置完成！
⚠️  重启后生效，或立即测试:
   /etc/aidlux/3.sh
   /etc/init.d/openclaw-gateway start
```

---

### 3. view_logs

**作用：** 查看 AidLux 启动日志和 Gateway 日志

**选项：**
- `--tail <num>` - 显示最后 N 行（默认 50）

**显示内容：**
1. AidLux Boot Log (`/var/log/aidlux/aidboot.log`) - 最近条目
2. Gateway Log (`/home/aidlux/.openclaw/gateway.log`) - 最后 N 行

**示例：**
```bash
node index.cjs view_logs --tail 100
```

---

### 4. diagnose

**作用：** 运行完整诊断，发现潜在问题并给出建议

**检查项：**
- 系统信息和环境
- Gateway 进程状态
- 自启动配置完整性
- 所有关键文件是否存在
- 路径检测是否正确

**输出：**
- 详细的状态检查结果（✅/❌）
- 发现的问题
- 具体的修复建议

**示例：**
```bash
=== 诊断报告 ===

--- 系统信息 ---
系统类型: Unknown
Node.js: v24.14.0
OpenClaw: 0.1.7-fix.1

--- 服务状态 ---
✅ Gateway 运行 (PID: 12213)
   命令: openclaw-termux

--- 自启动配置 ---
SysV init: 已启用
   /etc/rc2.d/S99openclaw-gateway
   /etc/rc3.d/S99openclaw-gateway
   /etc/rc4.d/S99openclaw-gateway
   /etc/rc5.d/S99openclaw-gateway
AidLux: 已配置
   /etc/aidlux/3.sh

--- 关键文件检查 ---
✅ PID 文件: /home/aidlux/.openclaw/gateway.pid
✅ 日志文件: /home/aidlux/.openclaw/gateway.log
✅ Init 脚本: /etc/init.d/openclaw-gateway
✅ AidLux 脚本: /etc/aidlux/3.sh
✅ Entry 文件: /home/aidlux/.nvm/versions/node/v24.14.0/lib/node_modules/openclaw-cn-termux/dist/entry.js
✅ 配置文件: /home/aidlux/.openclaw/openclaw.json

--- 建议 ---

=== 诊断完成 ===
```

---

### 5. full_setup

**作用：** 一键完成所有自启动配置

**执行流程：**
1. 调用 `enable_autostart --method=both`
2. 显示成功消息
3. 提示重启验证或立即测试

**示例：**
```bash
node index.cjs full_setup
```

---

## 🏗️ 技术架构

### 动态路径检测 (ConfigDetector)

**原理：** 自动识别环境中各组件的位置，无需硬编码路径

**检测项：**

| 检测目标 | 检测方法 |
|---------|---------|
| Node.js | `which node` → NVM 路径列表 → `process.execPath` |
| entry.js | 基于 nodePath 推断 → `npm root -g` → 标准位置 |
| PID 文件 | 读取 openclaw.json → 标准位置 → 扫描进程 |
| 日志文件 | 读取配置 → 标准位置 → 扫描目录 |
| 配置文件 | 标准位置 → 基于 entryPath 推断 |
| AidLux 3.sh | `/etc/aidlux/3.sh` 标准路径 |
| Init 脚本 | `/etc/init.d/openclaw-gateway` 标准路径 |
| rc?.d 链接 | 检查 rc2.d-rc5.d 目录 |
| AidLux 日志 | `/var/log/aidlux/aidboot.log` |

**缓存机制：** 所有检测结果缓存，避免重复计算。

---

## 📁 文件结构

```
/etc/aidlux/
└── 3.sh                          # AidLux 启动脚本（v3.0 极简版）

/etc/init.d/
└── openclaw-gateway               # SysV init 脚本

/etc/rc2.d/
├── S99openclaw-gateway -> ../init.d/openclaw-gateway
/etc/rc3.d/
├── S99openclaw-gateway -> ../init.d/openclaw-gateway
/etc/rc4.d/
├── S99openclaw-gateway -> ../init.d/openclaw-gateway
/etc/rc5.d/
└── S99openclaw-gateway -> ../init.d/openclaw-gateway

/home/aidlux/.openclaw/
├── gateway.pid                   # 进程 ID
├── gateway.log                   # 服务日志
└── openclaw.json                 # 配置文件

/var/log/aidlux/
└── aidboot.log                   # AidLux 启动日志
```

---

## 🚀 启动流程

```
System Boot
  └─> AidLux 0.sh
       └─> 启动 aidboot (Python Flask)
            └─> 扫描 /etc/aidlux/*.sh
                 └─> 执行 3.sh
                      └─> service openclaw-gateway restart
                           └─> /etc/init.d/openclaw-gateway start
                                └─> node entry.js gateway --port 18789
                                     └─> OpenClaw Gateway 运行
  └─> aidstarter (二进制)
       └─> 启动内置服务 (editonline, ttyd, vnc, sshd, filebrowser, desktop)
```

**注意：** 3.sh 在 `aidstarter` 之前执行，但 OpenClaw 不依赖这些服务，无需等待。

---

## ⚠️ 已知问题

1. **skill.yaml 与实现不一致**
   - `provides` 声明了 `disable_autostart` 和 `restart_gateway`
   - 但 `index.cjs` 未实现这些命令
   - **建议：** 更新 skill.yaml 或补全实现

2. **restart_gateway 缺失**
   - 目前需手动执行 `service openclaw-gateway restart`
   - 建议添加此命令到技能

---

## 🔄 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.0 | 2026-03-24 15:55 | 3.sh 改为极简版，复用 SysV init 脚本 |
| v2.0 | 2026-03-24 13:30 | 添加等待 aidstarter 完成的逻辑 |
| v1.0.1 | 2026-03-24 11:22 | 动态路径检测，修复兼容性问题 |
| v1.0.0 | 2026-03-24 11:22 | 初始版本 |

---

## 📝 测试验证

✅ **所有核心命令测试通过：**

```bash
# check_status - 显示完整状态
✅ 环境信息、服务状态、自启动配置、文件路径全部正确

# diagnose - 诊断报告
✅ 所有关键文件检查通过

# view_logs --tail 20
✅ 正确显示 aidboot.log 和 gateway.log

# enable_autostart --method=both
✅ 成功配置 SysV 和 AidLux 自启动

# full_setup
✅ 一键完成配置
```

---

**文档版本：** v3.0  
**最后更新：** 2026-03-24 16:14  
**作者：** 小新 🛠️
