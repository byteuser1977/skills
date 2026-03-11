/**
 * Indexer Module - Build and manage search cache
 */

const fs = require('fs');
const path = require('path');

const KNOWLEDGE_ROOT = path.resolve(process.env.KNOWLEDGE_ROOT || 'D:/workspace/clawd/knowledge/content/text');
const CACHE_FILE = path.resolve(process.env.CACHE_FILE || 'D:/workspace/clawd/state/search_cache.json');

/**
 * Get directory latest modification time
 */
function getDirMtime(dir) {
    let max = 0;
    try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            if (entry.isDirectory()) {
                const subMtime = getDirMtime(fullPath);
                if (subMtime > max) max = subMtime;
            } else {
                const stat = fs.statSync(fullPath);
                if (stat.mtimeMs > max) max = stat.mtimeMs;
            }
        }
    } catch (e) {}
    return max;
}

/**
 * Build file index
 */
function buildIndex() {
    const start = Date.now();
    const files = [];

    function walkDir(dir, relative = '') {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            const relPath = path.join(relative, entry.name);

            if (entry.isDirectory()) {
                walkDir(fullPath, relPath);
            } else if (entry.isFile() && entry.name.toLowerCase().endsWith('.md')) {
                try {
                    const stat = fs.statSync(fullPath);
                    files.push({
                        path: fullPath,
                        relPath: relPath,
                        name: entry.name,
                        size: stat.size,
                        mtime: stat.mtimeMs
                    });
                } catch (e) {
                    // Skip inaccessible files
                }
            }
        }
    }

    walkDir(KNOWLEDGE_ROOT);

    const cache = {
        timestamp: Date.now(),
        files: files
    };

    try {
        fs.mkdirSync(path.dirname(CACHE_FILE), { recursive: true });
        fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2), 'utf8');
    } catch (e) {
        console.warn('⚠️  Cannot write cache file:', e.message);
    }

    const elapsed = Date.now() - start;
    console.log(`🔄  Built index: ${files.length} files (${elapsed} ms)`);

    return cache;
}

/**
 * Load cache with freshness check
 */
function loadCache(forceRebuild = false) {
    if (!forceRebuild && fs.existsSync(CACHE_FILE)) {
        try {
            const cacheContent = fs.readFileSync(CACHE_FILE, 'utf8');
            const cache = JSON.parse(cacheContent);
            const indexTime = new Date(cache.timestamp).getTime();
            const rootMtime = getDirMtime(KNOWLEDGE_ROOT);

            // Cache valid for 7 days and knowledge base not modified
            if (Date.now() - indexTime < 7 * 24 * 60 * 60 * 1000 && rootMtime < indexTime) {
                return cache;
            }
            console.log(`⚠️  Cache expired or outdated, rebuilding...`);
        } catch (e) {
            console.warn('⚠️  Cache read error, rebuilding...');
        }
    }

    return buildIndex();
}

module.exports = {
    loadCache,
    buildIndex,
    getDirMtime
};
