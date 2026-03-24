/**
 * Abstract base class for all search providers
 * Based on Chatbox's base.ts
 */

export class BaseSearch {
  /**
   * Execute search query
   * @param {string} query - Search query
   * @param {AbortSignal} signal - Optional abort signal
   * @returns {Promise<{items: Array<{title, link, snippet, rawContent}>>}>}
   */
  async search(query, signal) {
    if (!query || typeof query !== 'string') {
      throw new Error('Query must be a non-empty string')
    }
    const trimmedQuery = query.trim()
    if (trimmedQuery.length === 0) {
      throw new Error('Query cannot be empty')
    }
    return this.executeSearch(trimmedQuery, signal)
  }

  /**
   * Override this method in subclass
   * @protected
   */
  async executeSearch(query, signal) {
    throw new Error('executeSearch must be implemented by subclass')
  }

  /**
   * Fetch helper (no mobile/Capacitor dependency, uses ofetch directly)
   */
  async fetch(url, options = {}) {
    const { method = 'GET', query = {}, body, headers = {} } = options

    const defaultHeaders = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1'
    }

    return await this.$fetch(url, {
      method,
      query,
      body,
      headers: { ...defaultHeaders, ...headers }
    })
  }

  /**
   * Internal fetch using ofetch
   * @private
   */
  async $fetch(url, options) {
    // Dynamic import of ofetch to avoid bundling issues
    let ofetch
    try {
      ofetch = (await import('ofetch')).ofetch
    } catch (e) {
      // Fallback to global fetch if ofetch not available
      const fetch = globalThis.fetch
      if (!fetch) throw new Error('No fetch implementation available')
      // Convert ofetch options to fetch
      const { method, query, body, headers } = options
      const urlObj = new URL(url)
      Object.keys(query).forEach(key => urlObj.searchParams.set(key, query[key]))
      const response = await fetch(urlObj.toString(), {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      return await response.text()
    }

    return await ofetch(url, options)
  }
}
