#!/bin/bash
#
# ColaMD Themes Wrapper Script
# 自动切换到 ColaMD-themes 项目根目录并执行 CLI 命令
#
# 使用方法：
#   ./colamd-themes-wrapper.sh from-url "https://example.com" -n "theme"
#   ./colamd-themes-wrapper.sh extract source.docx -A

set -e

# ColaMD-themes 项目根目录
PROJECT_ROOT="/Volumes/DATA/data/develop/git/ColaMD-themes"

if [ ! -d "$PROJECT_ROOT" ]; then
    echo "错误: ColaMD-themes 项目目录不存在: $PROJECT_ROOT" >&2
    exit 1
fi

cd "$PROJECT_ROOT"

if [ ! -f "dist/cli.js" ] && [ ! -f "src/cli.ts" ]; then
    echo "错误: 未找到 ColaMD-themes CLI 入口文件" >&2
    exit 1
fi

if [ ! -d "node_modules" ]; then
    echo "警告: node_modules 不存在，请先运行 npm install" >&2
fi

if [ -f "dist/cli.js" ]; then
    CMD="node dist/cli.js"
else
    CMD="npx tsx src/cli.ts"
fi

$CMD "$@"
