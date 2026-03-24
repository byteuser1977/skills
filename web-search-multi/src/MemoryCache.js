/**
 * Simple in-memory cache with TTL
 * Implements similar behavior to Chatbox's cache Map
 */

export class MemoryCache {
  constructor(ttl = 5 * 60 * 1000) {
    this.ttl = ttl
    this.cache = new Map()
  }

  /**
   * Get cached value if still valid
   * @param {string} key
   * @returns {Object|null} - { result, timestamp }
   */
  get(key) {
    const entry = this.cache.get(key)
    if (!entry) return null

    if (Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(key)
      return null
    }

    return entry
  }

  /**
   * Set cached value
   * @param {string} key
   * @param {*} result
   */
  set(key, result) {
    this.cache.set(key, {
      result,
      timestamp: Date.now()
    })

    // Simple cleanup: keep cache size under 1000
    if (this.cache.size > 1000) {
      const firstKey = this.cache.keys().next().value
      if (firstKey) this.cache.delete(firstKey)
    }
  }

  /**
   * Clear all entries
   */
  clear() {
    this.cache.clear()
  }

  /**
   * Get current size
   */
  size() {
    return this.cache.size
  }
}
