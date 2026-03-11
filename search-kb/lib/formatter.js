/**
 * Formatter Module - Output formatting and highlighting
 */

const fs = require('fs');

// ANSI color codes (no external dependencies)
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    dim: '\x1b[2m',
    cyan: '\x1b[36m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    magenta: '\x1b[35m',
    gray: '\x1b[90m',
    red: '\x1b[31m'
};

/**
 * Highlight keyword in text (ANSI colors)
 */
function highlight(text, keyword) {
    if (!keyword) return text;
    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escaped})`, 'gi');
    return text.replace(regex, '\x1b[93m$1\x1b[0m'); // Yellow
}

/**
 * Format and print results
 */
function displayResults(results, keyword, context = 2) {
    console.log(`🎯 找到 ${results.length} 个文件包含 "${keyword}"\n`);
    console.log('─'.repeat(80));

    for (const result of results) {
        console.log(`\n${colors.magenta}📄 ${result.relPath}${colors.reset} ${colors.dim}(${result.matchCount} 处匹配)${colors.reset}`);

        try {
            const allLines = fs.readFileSync(result.path, 'utf8').split(/\r?\n/);
            const shown = new Set();

            // Show up to first 3 matches per file
            result.matches.slice(0, 3).forEach(match => {
                const start = Math.max(1, match.line - context);
                const end = Math.min(allLines.length, match.line + context);

                for (let i = start; i <= end; i++) {
                    if (shown.has(i)) continue;
                    shown.add(i);

                    const prefix = i === match.line ? '>>>' : '   ';
                    let lineText = allLines[i - 1].trim();
                    if (i === match.line) {
                        lineText = highlight(lineText, keyword);
                    }
                    // Truncate long lines
                    if (lineText.length > 120) {
                        lineText = lineText.substring(0, 120) + '...';
                    }
                    console.log(`${prefix} ${String(i).padStart(5, ' ')} | ${lineText}`);
                }
                console.log('');
            });
        } catch (e) {
            console.log(`   [${colors.red}错误: 无法读取文件${colors.reset}]`);
        }
    }

    console.log('─'.repeat(80));
    console.log(`📊 搜索结果总计: ${colors.bright}${results.length}${colors.reset} 个文件`);
}

/**
 * Print summary header
 */
function printHeader(keyword, cache, useCache) {
    if (useCache) {
        const date = new Date(cache.timestamp).toLocaleDateString();
        console.log(`✅ 使用缓存索引（${cache.files.length} 个文件，更新于 ${date}）`);
    }
    console.log(`🔍 搜索关键词: "${keyword}"`);
    console.log(`📂 知识库目录: ${process.env.KNOWLEDGE_ROOT || 'D:/workspace/clawd/knowledge/content/text'}`);
    console.log('⏳ 请稍候...\n');
}

/**
 * Format results as JSON
 */
function formatJSON(keyword, cache, results) {
    const output = {
        query: keyword,
        timestamp: new Date().toISOString(),
        cacheInfo: {
            totalFiles: cache.files.length,
            builtAt: cache.timestamp
        },
        totalResults: results.length,
        results: results.map(r => ({
            relativePath: r.relPath,
            name: r.name,
            size: r.size,
            matchCount: r.matchCount,
            bestScore: r.bestScore,
            matches: r.matches.slice(0, 5) // only first 5 matches
        }))
    };
    return JSON.stringify(output, null, 2);
}

/**
 * Format results as CSV
 */
function formatCSV(results) {
    const headers = ['相对路径', '文件名', '大小(B)', '匹配数', '最高分'];
    const rows = results.map(r => [
        r.relPath,
        r.name,
        r.size,
        r.matchCount,
        r.bestScore
    ]);

    // Simple CSV with UTF-8 BOM for Excel compatibility
    const bom = '\uFEFF';
    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    return bom + csvContent;
}

module.exports = {
    displayResults,
    printHeader,
    highlight,
    formatJSON,
    formatCSV
};
