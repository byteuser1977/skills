#!/bin/bash
#
# ColaMD Themes Wrapper Script
# 通过 npx 或全局安装的 colamd-themes 命令执行 CLI 操作
#
# 使用前请赋予执行权限:
#   chmod +x scripts/colamd-themes-wrapper.sh
#
# 使用方法：
#   ./scripts/colamd-themes-wrapper.sh from-url "https://example.com" -n "theme"
#   ./scripts/colamd-themes-wrapper.sh extract source.docx -A
#
# 优先级：全局安装 > npx

set -e

# 检查 colamd-themes 是否已全局安装
if command -v colamd-themes &> /dev/null; then
    CMD="colamd-themes"
elif command -v cthemes &> /dev/null; then
    CMD="cthemes"
else
    # 使用 npx 运行
    CMD="npx @bytechain.cn/colamd-themes"
fi

$CMD "$@"
