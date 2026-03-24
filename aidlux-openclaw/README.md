# AidLux OpenClaw Gateway Skill

**AidLux 环境下 OpenClaw 相关的工具**
- 自启动服务安装
- 系统环境检测

管理 OpenClaw Gateway 在 AidLux 系统中的守护进程配置。

## 快速开始

```bash
# 1. 安装自启动
node index.cjs install

# 2. 检查环境
node index.cjs check_env

# 3. 查看帮助
node index.cjs --help
```

## 功能

- ✅ **install** - 安装自启动（生成 `/etc/aidlux/3.sh` 和 rc?.d 符号链接）
- ✅ **check_env** - 检查运行环境（which 检测路径，结果保存到 memory）

## 命令详解

### install

安装 OpenClaw Gateway 到 AidLux 自启动系统。

**操作：**
1. 检测 `openclaw-termux` 命令
2. 检测 `service` 命令
3. 创建 `/etc/aidlux/3.sh` (v3.0 极简版)
4. 创建 SysV init 符号链接 (rc2.d-rc5.d)
5. 立即测试启动

**示例：**
```bash
node index.cjs install
```

**输出：**
```
=== 安装 OpenClaw 自启动 ===
✅ 检测到 OpenClaw 命令: ...
✅ 检测到 service 命令
✅ 已创建 /etc/aidlux/3.sh
✅ 符号链接已存在: /etc/rc2.d/S99openclaw-gateway
...
✅ 自启动安装完成！
```

---

### check_env

检查 AidLux 运行环境，检测关键命令路径，结果保存到 memory 目录。

**检测内容：**
- 系统信息 (uname, kernel)
- 命令路径: node, npm, python3, service, openclaw-termux
- Node.js 版本
- OpenClaw entry.js 位置
- AidLux 启动脚本 (0.sh, 1.sh, 2.sh, 3.sh)

**示例：**
```bash
node index.cjs check_env
```

**输出：**
```
=== 检查运行环境 ===
--- 命令路径检测 ---
✅ node: /home/aidlux/.nvm/versions/node/v24.14.0/bin/node
✅ npm: /home/aidlux/.nvm/versions/node/v24.14.0/bin/npm
...
✅ 检测结果已保存: memory/aidlux-env-2026-03-24.md
✅ 已更新 memory.md
```

**生成文件：**
- `memory/aidlux-env-YYYY-MM-DD.md` - 详细检测报告
- `memory.md` - 自动插入摘要

---

## 3.sh 内容 (v3.0 极简版)

```bash
#!/bin/bash
# THIS FILE IS RESERVED FOR AIDLUX TO START OPENCLAW GATEWAY
echo "Starting OpenClaw Gateway..."
nohup service openclaw-gateway restart >/dev/null 2>&1 &
if [ -f /boot/aidlux/aidfunc ]; then
    source /boot/aidlux/aidfunc 2>/dev/null
    type aidlog &>/dev/null && aidlog "OpenClaw Gateway started by /etc/aidlux/3.sh"
fi
```

**设计思想：** 复用 SysV init 脚本，8 行代码完成集成，不硬编码路径。

---

## 文件结构

```
/etc/aidlux/
└── 3.sh                          # AidLux 启动脚本 (v3.0)

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

memory/
├── aidlux-env-YYYY-MM-DD.md      # 环境检测报告
└── ... (其他 daily memory 文件)
```

---

## 启动流程

```
System Boot
  └─> AidLux 0.sh
       └─> 启动 aidboot
            └─> 扫描 /etc/aidlux/*.sh
                 └─> 执行 3.sh
                      └─> service openclaw-gateway restart
                           └─> /etc/init.d/openclaw-gateway start
                                └─> node entry.js gateway --port 18789
                                     └─> OpenClaw Gateway 运行
```

---

## 帮助

```bash
node index.cjs --help
```

输出：
```
AidLux OpenClaw Gateway Skill (简化版)

用法:
  aidlux-openclaw <command> [options]

命令:
  install      安装自启动（生成 3.sh 和 rc?.d 链接）
  check_env    检查运行环境（检测路径并保存到 memory）

示例:
  aidlux-openclaw install
  aidlux-openclaw check_env
```

---

## 开发信息

- **开发人员:** byteuser
- **版本:** 1.0.0
- **创建日期:** 2026-03-24
- **许可:** MIT

---

**注意：** 此 Skill 专为 AidLux 环境设计，需要在 Android/Termux 上运行 OpenClaw。
