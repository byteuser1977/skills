#!/bin/bash
#
# ColaMD Themes Wrapper Script
# 自动切换到 ColaMD-themes 项目根目录并执行 CLI 命令
#
# 使用方法：
#   ./colamd-themes-wrapper.sh from-url "https://example.com" -n "theme"
#   ./colamd-themes-wrapper.sh extract source.docx -A
#
# 注意：需要预先在 ColaMD-themes 项目目录运行 npm install && npm run build

set -e

# ColaMD-themes 项目根目录
PROJECT_ROOT="/mnt/d/workspace/git/ColaMD-themes"

# 检查项目目录是否存在
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "错误: ColaMD-themes 项目目录不存在: $PROJECT_ROOT" >&2
    exit 1
fi

# 切换到项目目录
cd "$PROJECT_ROOT"

# 检查是否需要编译
if [ ! -f "dist/cli.js" ] && [ ! -f "src/cli.ts" ]; then
    echo "错误: 未找到 ColaMD-themes CLI 入口文件" >&2
    exit 1
fi

# 如果存在 node_modules，说明依赖已安装；否则提示
if [ ! -d "node_modules" ]; then
    echo "警告: node_modules 不存在，请先运行 npm install" >&2
fi

# 如果已编译，使用编译版本；否则使用 tsx 直接运行
if [ -f "dist/cli.js" ]; then
    CMD="node dist/cli.js"
else
    CMD="npx tsx src/cli.ts"
fi

# 执行命令，传递所有参数
echo "执行: $CMD $*"
$CMD "$@"
