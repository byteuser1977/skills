/**
 * Searcher Module - Full-text search logic
 */

const fs = require('fs');

/**
 * Calculate relevance score
 */
function scoreMatch(file, keyword, line) {
    let score = 0;
    const kw = keyword.toLowerCase();
    const lineLower = line.toLowerCase();

    // 1. Filename match (highest weight)
    if (file.name.toLowerCase().includes(kw)) score += 100;

    // 2. Path match (medium weight)
    if (file.relPath.toLowerCase().includes(kw)) score += 50;

    // 3. Heading/emphasis match (high weight)
    if (/^(#+|\*\*|>|```)/i.test(line.trim())) score += 30;

    // 4. Multiple occurrences (low weight)
    const matches = (lineLower.match(new RegExp(kw, 'gi')) || []).length;
    score += matches;

    return score;
}

/**
 * Check if file passes all filters
 */
function passesFilters(file, filters) {
    const { filterDir, minSize, maxSize, mtimeAfter, mtimeBefore } = filters;

    // Directory filter
    if (filterDir) {
        const filterDirLower = filterDir.toLowerCase();
        if (!file.relPath.toLowerCase().includes(filterDirLower)) {
            return false;
        }
    }

    // File size filter (size in bytes)
    if (minSize !== null && file.size < minSize * 1024) {
        return false;
    }
    if (maxSize !== null && file.size > maxSize * 1024) {
        return false;
    }

    // Modification time filter (timestamp in ms)
    if (mtimeAfter !== null && file.mtime < mtimeAfter) {
        return false;
    }
    if (mtimeBefore !== null && file.mtime > mtimeBefore) {
        return false;
    }

    return true;
}

/**
 * Execute search
 */
function search(cache, keyword, options = {}) {
    const {
        limit = 50,
        filterDir = null,
        minSize = null,
        maxSize = null,
        mtimeAfter = null,
        mtimeBefore = null
    } = options;

    const results = [];
    const keywordLower = keyword.toLowerCase();

    for (const file of cache.files) {
        // Apply filters first (skip expensive read if filtered out)
        if (!passesFilters(file, { filterDir, minSize, maxSize, mtimeAfter, mtimeBefore })) {
            continue;
        }

        try {
            const content = fs.readFileSync(file.path, 'utf8');
            const lines = content.split(/\r?\n/);
            const matches = [];

            lines.forEach((line, idx) => {
                if (line.toLowerCase().includes(keywordLower)) {
                    matches.push({
                        line: idx + 1,
                        text: line.trim()
                    });
                }
            });

            if (matches.length > 0) {
                // Get best score
                const bestScore = Math.max(...matches.map(m => scoreMatch(file, keyword, m.text)));
                results.push({
                    ...file,
                    matchCount: matches.length,
                    bestLine: matches[0].line,
                    bestScore: bestScore,
                    matches: matches
                });
            }
        } catch (e) {
            // Skip read errors
        }
    }

    // Sort by relevance
    results.sort((a, b) => b.bestScore - a.bestScore);

    return results.slice(0, limit);
}

module.exports = {
    search,
    scoreMatch,
    passesFilters
};
