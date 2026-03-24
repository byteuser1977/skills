/**
 * Tavily Search Provider (API-based)
 * Based on Chatbox's tavily.ts
 */
import { BaseSearch } from './base.js'

export class TavilySearch extends BaseSearch {
  static TAVILY_SEARCH_URL = 'https://api.tavily.com/search'

  constructor(config = {}) {
    super()
    this.apiKey = config.apiKey
    this.searchDepth = config.searchDepth || 'basic'
    this.maxResults = config.maxResults || 5
    this.timeRange = config.timeRange === 'none' ? null : config.timeRange
    this.includeRawContent = config.includeRawContent === 'none' ? null : config.includeRawContent
  }

  async executeSearch(query, signal) {
    if (!this.apiKey) {
      throw new Error('Tavily API key is required')
    }

    try {
      const requestBody = this.buildRequestBody(query)
      const response = await this.fetch(TavilySearch.TAVILY_SEARCH_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: requestBody,
        signal
      })

      // Parse JSON response
      const data = typeof response === 'string' ? JSON.parse(response) : response

      const items = (data.results || []).map(result => ({
        title: result.title || '',
        link: result.url || '',
        snippet: result.content || '',
        rawContent: result.raw_content || null
      }))

      return { items }
    } catch (error) {
      console.error('Tavily search error:', error)
      return { items: [] }
    }
  }

  buildRequestBody(query) {
    const requestBody = {
      query,
      search_depth: this.searchDepth,
      max_results: this.maxResults,
      include_domains: [],
      exclude_domains: []
    }

    if (this.timeRange) {
      requestBody.time_range = this.timeRange
    }

    if (this.includeRawContent) {
      requestBody.include_raw_content = this.includeRawContent
    }

    return requestBody
  }
}
