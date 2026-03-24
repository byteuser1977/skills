/**
 * Multi-Search Orchestrator
 * Parallel execution + round-robin merging
 *
 * Based on Chatbox's _searchRelatedResults function
 */

import { truncate } from './truncate.js'

export class MultiSearch {
  constructor(providers = [], options = {}) {
    this.providers = providers
    this.maxResults = options.maxResults || 10
    this.snippetLength = options.snippetLength || 150
    this.cache = options.cache || null
    this.cacheTtl = options.cacheTtl || 5 * 60 * 1000 // 5 minutes
  }

  /**
   * Execute search across all providers
   * @param {string} query
   * @param {AbortSignal} signal
   * @returns {Promise<Array<{title, snippet, link, rawContent}>>}
   */
  async search(query, signal) {
    if (!query || typeof query !== 'string') {
      throw new Error('Query must be a non-empty string')
    }

    const trimmedQuery = query.trim()
    if (!trimmedQuery) {
      throw new Error('Query cannot be empty')
    }

    // Check cache
    if (this.cache) {
      const cached = this.cache.get(trimmedQuery)
      if (cached && Date.now() - cached.timestamp < this.cacheTtl) {
        return cached.result
      }
    }

    // Execute all providers in parallel
    const results = await Promise.all(
      this.providers.map(async (provider) => {
        try {
          const result = await provider.search(trimmedQuery, signal)
          return result
        } catch (error) {
          console.error('Provider search failed:', error.message)
          return { items: [] }
        }
      })
    )

    // Interleave results (round-robin)
    const mergedItems = this.interleave(results, this.maxResults)

    // Apply truncation to snippets
    const finalItems = mergedItems.map(item => ({
      title: item.title,
      snippet: truncate(item.snippet, { length: this.snippetLength }),
      link: item.link,
      rawContent: item.rawContent
    }))

    // Cache result
    if (this.cache) {
      this.cache.set(trimmedQuery, {
        result: finalItems,
        timestamp: Date.now()
      })
    }

    return finalItems
  }

  /**
   * Interleave multiple result arrays (round-robin)
   * @private
   */
  interleave(results, maxItems) {
    const items = []
    let i = 0
    let hasMore = false

    do {
      hasMore = false
      for (const result of results) {
        if (result.items && result.items[i]) {
          hasMore = true
          items.push(result.items[i])
        }
      }
      i++
    } while (hasMore && items.length < maxItems)

    return items
  }
}
