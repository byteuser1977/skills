#!/usr/bin/env node

/**
 * AidLux OpenClaw Gateway Skill (简化版)
 * 命令：install, check_env
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// ============================================
// 工具函数
// ============================================

function which(cmd) {
  try {
    return execSync(`which ${cmd}`, { encoding: 'utf-8' }).trim();
  } catch (e) {
    // 尝试常见路径
    const commonPaths = [
      '/sbin/service',
      '/usr/sbin/service',
      '/bin/service',
      '/usr/bin/service'
    ];
    for (const p of commonPaths) {
      if (fs.existsSync(p)) return p;
    }
    return null;
  }
}

function getCurrentDate() {
  return new Date().toISOString().split('T')[0]; // YYYY-MM-DD
}

function ensureMemoryDir() {
  const memoryDir = path.join(process.cwd(), 'memory');
  if (!fs.existsSync(memoryDir)) {
    fs.mkdirSync(memoryDir, { recursive: true });
  }
  return memoryDir;
}

function updateMemoryMD(summary) {
  try {
    const memoryMdPath = path.join(process.cwd(), 'memory.md');
    if (!fs.existsSync(memoryMdPath)) return;

    const original = fs.readFileSync(memoryMdPath, 'utf-8');
    const today = getCurrentDate();
    const section = `\n## AidLux 环境检测 (${today})\n\n${summary}\n`;

    // 插入到文件开头或 Current Status 之后
    const insertIndex = original.indexOf('## Current Status');
    if (insertIndex !== -1) {
      const nextSection = original.indexOf('\n## ', insertIndex + 1);
      if (nextSection !== -1) {
        const updated = original.slice(0, nextSection) + section + original.slice(nextSection);
        fs.writeFileSync(memoryMdPath, updated, 'utf-8');
        console.log('✅ 已更新 memory.md');
      }
    }
  } catch (err) {
    console.warn('⚠️  更新 memory.md 失败:', err.message);
  }
}

// ============================================
// 命令 1: install - 安装自启动
// ============================================

function cmdInstall() {
  console.log('\n=== 安装 OpenClaw 自启动 ===\n');

  // 1. 检测 openclaw-termux 命令
  const openclawCmd = which('openclaw-termux') || which('clawdbot-gateway');
  if (!openclawCmd) {
    console.error('❌ 未找到 openclaw-termux 或 clawdbot-gateway 命令');
    console.error('   请确认 OpenClaw 已正确安装');
    process.exit(1);
  }
  console.log(`✅ 检测到 OpenClaw 命令: ${openclawCmd}`);

  // 2. 检测 service 命令
  if (!which('service')) {
    console.error('❌ 未找到 service 命令');
    process.exit(1);
  }
  console.log('✅ 检测到 service 命令');

  // 3. 创建 3.sh 内容 (v3.0 极简版)
  const script3 = `#!/bin/bash
# THIS FILE IS RESERVED FOR AIDLUX TO START OPENCLAW GATEWAY
echo "Starting OpenClaw Gateway..."
nohup service openclaw-gateway restart >/dev/null 2>&1 &
if [ -f /boot/aidlux/aidfunc ]; then
    source /boot/aidlux/aidfunc 2>/dev/null
    type aidlog &>/dev/null && aidlog "OpenClaw Gateway started by /etc/aidlux/3.sh"
fi
`;

  // 4. 写入 /etc/aidlux/3.sh
  const scriptPath = '/etc/aidlux/3.sh';
  try {
    fs.writeFileSync(scriptPath, script3, 'utf-8');
    fs.chmodSync(scriptPath, 0o755);
    console.log(`✅ 已创建 ${scriptPath}`);
  } catch (err) {
    if (err.code === 'EACCES') {
      console.error('❌ 权限不足，需要 root 权限写入 /etc/aidlux/');
      console.error(`   请手动运行: sudo sh -c 'cat > ${scriptPath} <<EOF'`);
      console.error(script3);
      console.error('EOF');
      process.exit(1);
    }
    throw err;
  }

  // 5. 配置 SysV init 符号链接
  const initScript = '/etc/init.d/openclaw-gateway';
  if (!fs.existsSync(initScript)) {
    console.warn('⚠️  未找到 init.d 脚本，跳过 SysV init 配置');
  } else {
    const levels = [2, 3, 4, 5];
    let created = 0;
    levels.forEach(level => {
      const link = `/etc/rc${level}.d/S99openclaw-gateway`;
      try {
        fs.symlinkSync(initScript, link);
        console.log(`✅ 创建符号链接: ${link}`);
        created++;
      } catch (err) {
        if (err.code === 'EEXIST') {
          console.log(`✅ 符号链接已存在: ${link}`);
          created++;
        } else if (err.code === 'EPERM') {
          console.warn(`⚠️  权限不足，无法创建: ${link}`);
        } else {
          console.warn(`⚠️  无法创建: ${link} (${err.message})`);
        }
      }
    });
    if (created > 0) {
      console.log(`✅ SysV init 配置完成 (${created} 个运行级别)`);
    }
  }

  // 6. 立即测试
  console.log('\n--- 立即测试 ---');
  try {
    execSync(`${scriptPath}`, { stdio: 'inherit' });
  } catch (err) {
    console.error('❌ 3.sh 执行失败:', err.message);
  }

  console.log('\n✅ 自启动安装完成！');
  console.log('   重启系统后将自动启动 OpenClaw Gateway');
}

// ============================================
// 命令 2: check_env - 检查运行环境
// ============================================

function cmdCheckEnv() {
  console.log('\n=== 检查运行环境 ===\n');

  const memoryDir = ensureMemoryDir();
  const today = getCurrentDate();
  const memoryFile = path.join(memoryDir, `aidlux-env-${today}.md`);

  const info = {
    检测时间: new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' }),
    系统: {},
    命令路径: {},
    Node: {},
    OpenClaw: {},
    AidLux: {}
  };

  // 1. 系统信息
  try {
    info.系统.uname = execSync('uname -a', { encoding: 'utf-8' }).trim();
  } catch (e) {
    info.系统.uname = 'unknown';
  }

  try {
    const release = fs.readFileSync('/proc/version', 'utf-8').trim();
    info.系统.kernel = release.substring(0, 100);
  } catch (e) {
    info.系统.kernel = 'unknown';
  }

  // 2. 关键命令路径（which 检测）
  const commands = ['node', 'npm', 'python3', 'service', 'openclaw-termux', 'clawdbot-gateway'];
  console.log('--- 命令路径检测 ---');
  commands.forEach(cmd => {
    const path = which(cmd);
    if (path) {
      info.命令路径[cmd] = path;
      console.log(`✅ ${cmd}: ${path}`);
    } else {
      info.命令路径[cmd] = null;
      console.log(`❌ ${cmd}: 未找到`);
    }
  });

  // 3. Node.js 版本
  if (info.命令路径.node) {
    try {
      info.Node.版本 = execSync('node --version', { encoding: 'utf-8' }).trim();
    } catch (e) {}
  }
  if (info.命令路径.npm) {
    try {
      info.Node.npm版本 = execSync('npm --version', { encoding: 'utf-8' }).trim();
    } catch (e) {}
  }

  // 4. OpenClaw 信息
  const entryCandidates = [];
  if (info.命令路径.node) {
    const nodeBin = path.dirname(info.命令路径.node);
    const nodeRoot = path.join(nodeBin, '..');
    entryCandidates.push(
      path.join(nodeRoot, 'lib', 'node_modules', 'openclaw-cn-termux', 'dist', 'entry.js'),
      path.join(nodeRoot, 'lib', 'node_modules', 'openclaw-cn-termux', 'entry.js')
    );
  }
  // 全局 npm root
  try {
    const npmRoot = execSync('npm root -g', { encoding: 'utf-8' }).trim();
    entryCandidates.push(path.join(npmRoot, 'openclaw-cn-termux', 'dist', 'entry.js'));
  } catch (e) {}

  // 已知路径
  entryCandidates.push(
    '/home/aidlux/.nvm/versions/node/v24.14.0/lib/node_modules/openclaw-cn-termux/dist/entry.js'
  );

  info.OpenClaw.entryPath = null;
  for (const p of entryCandidates) {
    if (p && fs.existsSync(p)) {
      info.OpenClaw.entryPath = p;
      break;
    }
  }
  if (info.OpenClaw.entryPath) {
    console.log(`✅ entry.js: ${info.OpenClaw.entryPath}`);
  } else {
    console.log('❌ 未找到 entry.js');
  }

  // 5. AidLux 脚本
  const aidluxScripts = ['/etc/aidlux/0.sh', '/etc/aidlux/1.sh', '/etc/aidlux/2.sh', '/etc/aidlux/3.sh'];
  info.AidLux.scripts = [];
  console.log('\n--- AidLux 脚本 ---');
  aidluxScripts.forEach(script => {
    if (fs.existsSync(script)) {
      try {
        const stat = fs.statSync(script);
        info.AidLux.scripts.push({
          path: script,
          size: stat.size,
          mtime: stat.mtime.toISOString()
        });
        console.log(`✅ ${script} (${stat.size} bytes)`);
      } catch (e) {}
    } else {
      console.log(`❌ ${script} 不存在`);
    }
  });

  // 6. 生成 Markdown 报告
  let md = `# AidLux 环境检测报告\n\n`;
  md += `**检测时间:** ${info.检测时间}\n\n`;

  md += `## 系统信息\n\n`;
  md += `- **uname:** \`${info.系统.uname}\`\n`;
  md += `- **kernel:** \`${info.系统.kernel}\`\n\n`;

  md += `## 命令路径\n\n`;
  Object.entries(info.命令路径).forEach(([cmd, path]) => {
    md += `- **${cmd}:** ${path ? `\`${path}\`` : '❌ 未找到'}\n`;
  });
  md += '\n';

  md += `## Node.js\n\n`;
  if (info.Node.版本) {
    md += `- **版本:** ${info.Node.版本}\n`;
  }
  if (info.Node.npm版本) {
    md += `- **npm:** ${info.Node.npm版本}\n`;
  }
  md += '\n';

  md += `## OpenClaw\n\n`;
  if (info.OpenClaw.entryPath) {
    md += `- **entry.js:** \`${info.OpenClaw.entryPath}\`\n`;
  } else {
    md += `- **entry.js:** ❌ 未找到\n`;
  }
  md += '\n';

  if (info.AidLux.scripts.length > 0) {
    md += `## AidLux 启动脚本\n\n`;
    info.AidLux.scripts.forEach(s => {
      md += `- \`${s.path}\` (${s.size} bytes, 修改: ${s.mtime})\n`;
    });
    md += '\n';
  }

  try {
    fs.writeFileSync(memoryFile, md, 'utf-8');
    console.log(`\n✅ 检测结果已保存: ${memoryFile}`);
  } catch (err) {
    console.error('❌ 保存检测结果失败:', err.message);
    return;
  }

  // 生成 summary 并更新 memory.md
  const summaryLines = [
    `- 检测时间: ${info.检测时间}`,
    `- 系统: ${info.系统.uname?.split(' ')[0] || 'Unknown'}`,
    `- Node.js: ${info.Node.版本 || 'Unknown'}`,
    `- OpenClaw entry: ${info.OpenClaw.entryPath ? '已找到' : '未找到'}`,
    `- 详情: memory/aidlux-env-${today}.md`
  ];
  updateMemoryMD(summaryLines.join('\n'));

  console.log('\n=== 环境检查完成 ===\n');
}

// ============================================
// 主入口
// ============================================

function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';

  switch (command) {
    case 'install':
      cmdInstall();
      break;
    case 'check_env':
      cmdCheckEnv();
      break;
    case '--help':
    case '-h':
    case 'help':
      console.log(`
AidLux OpenClaw Gateway Skill (简化版)

用法:
  aidlux-openclaw <command> [options]

命令:
  install      安装自启动（生成 3.sh 和 rc?.d 链接）
  check_env    检查运行环境（检测路径并保存到 memory）

示例:
  aidlux-openclaw install
  aidlux-openclaw check_env

说明:
  - install: 创建 /etc/aidlux/3.sh（极简版）和 SysV init 符号链接
  - check_env: 使用 which 检测关键命令路径，结果保存到 memory/
`);
      break;
    default:
      console.log(`❌ 未知命令: ${command}`);
      console.log('使用 --help 查看帮助');
      process.exit(1);
  }
}

main();
