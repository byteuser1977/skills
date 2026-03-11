#!/usr/bin/env node

/**
 * Search Knowledge Base - OpenClaw Skill
 *
 * Usage via OpenClaw:
 *   npx skills run search-kb "keyword" --limit 20 --context 2
 *
 * Or directly:
 *   node bin/search-kb.js "keyword" --limit 20
 */

const path = require('path');

// Compute absolute paths based on this file's location
const skillRoot = path.resolve(__dirname, '..');

// Build absolute paths to library modules
const indexerPath = path.resolve(skillRoot, 'lib', 'indexer');
const searcherPath = path.resolve(skillRoot, 'lib', 'searcher');
const formatterPath = path.resolve(skillRoot, 'lib', 'formatter');

let loadCache, buildIndex, search, displayResults, printHeader, formatJSON, formatCSV;

try {
    // Load modules
    const indexer = require(indexerPath);
    const searcher = require(searcherPath);
    const formatter = require(formatterPath);

    loadCache = indexer.loadCache;
    buildIndex = indexer.buildIndex;
    search = searcher.search;
    displayResults = formatter.displayResults;
    printHeader = formatter.printHeader;
    formatJSON = formatter.formatJSON;
    formatCSV = formatter.formatCSV;
} catch (err) {
    console.error(`❌ 模块加载失败:`);
    console.error(`   indexerPath: ${indexerPath}`);
    console.error(`   searcherPath: ${searcherPath}`);
    console.error(`   formatterPath: ${formatterPath}`);
    console.error(`   error: ${err.message}`);
    process.exit(1);
}

// Parse arguments
const args = process.argv.slice(2);

if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`
🚀 Search Knowledge Base Skill

用法:
  npx skills run search-kb "关键词" [选项]
  或
  node bin/search-kb.js "关键词" [选项]

选项:
  --limit <N>          最大显示结果数 (默认: 50)
  --context <N>        显示匹配行前后各行数 (默认: 2)
  --output <format>   输出格式: text, json, csv (默认: text)
  --filter-dir <path>  仅搜索指定目录 (相对知识库根)
  --min-size <KB>     最小文件大小 (KB)
  --max-size <KB>     最大文件大小 (KB)
  --mtime-after <ts>  仅搜索修改时间晚于时间戳的文件 (毫秒)
  --mtime-before <ts> 仅搜索修改时间早于时间戳的文件 (毫秒)
  --no-cache          禁用缓存
  --rebuild           强制重建缓存
  --help, -h          显示此帮助

示例:
  # 基础搜索
  search-kb "项目管理"

  # 限制数量并增加上下文
  search-kb "信贷" --limit 20 --context 3

  # 只搜索 TATA 培训资料中的风险管理
  search-kb "Risk Management" --filter-dir "TATA/File/资料/Academy Certification/Risk Management"

  # 搜索大型文件 (>50KB) 并按大小过滤
  search-kb "架构" --min-size 50 --max-size 500

  # 导出为 JSON 供程序处理
  search-kb "支付系统" --output json --limit 100 > payments.json

  # 导出为 CSV 用 Excel 打开
  search-kb "授权" --output csv > auth_report.csv

    `.trim());
    process.exit(0);
}

const keyword = args[0];

// Parse options
const getOptionValue = (flag, defaultValue) => {
    const idx = args.indexOf(flag);
    if (idx !== -1 && idx + 1 < args.length && !args[idx + 1].startsWith('--')) {
        return args[idx + 1];
    }
    return defaultValue;
};

const limit = parseInt(getOptionValue('--limit', '50'), 10);
const context = parseInt(getOptionValue('--context', '2'), 10);
const outputFormat = getOptionValue('--output', 'text'); // text, json, csv
const filterDir = getOptionValue('--filter-dir', null);
const minSize = getOptionValue('--min-size', null) ? parseInt(getOptionValue('--min-size'), 10) : null;
const maxSize = getOptionValue('--max-size', null) ? parseInt(getOptionValue('--max-size'), 10) : null;
const mtimeAfter = getOptionValue('--mtime-after', null) ? parseInt(getOptionValue('--mtime-after'), 10) : null;
const mtimeBefore = getOptionValue('--mtime-before', null) ? parseInt(getOptionValue('--mtime-before'), 10) : null;

const useCache = !args.includes('--no-cache');
const rebuildCache = args.includes('--rebuild');

try {
    // Load or build cache
    const cache = loadCache(rebuildCache);
    printHeader(keyword, cache, useCache && !rebuildCache);

    // Perform search with filters
    const results = search(cache, keyword, {
        limit,
        filterDir,
        minSize,
        maxSize,
        mtimeAfter,
        mtimeBefore
    });

    // Display results based on output format
    if (outputFormat === 'json') {
        console.log(formatJSON(keyword, cache, results));
    } else if (outputFormat === 'csv') {
        console.log(formatCSV(results));
    } else {
        displayResults(results, keyword, context);
    }

} catch (error) {
    console.error('❌ 搜索失败:', error.message);
    process.exit(1);
}
