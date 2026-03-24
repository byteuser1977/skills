/**
 * Bing Search Provider
 * Based on Chatbox's bing.ts
 */
import { BaseSearch } from './base.js'
import { parse } from 'node-html-parser'

export class BingSearch extends BaseSearch {
  async executeSearch(query, signal) {
    const html = await this.fetchSerp(query, signal)
    const items = this.extractItems(html)
    return { items }
  }

  async fetchSerp(query, signal) {
    const url = 'https://www.bing.com/search'
    const params = {
      q: query,
      form: 'QBLH',
      sp: '-1', // Global search, no location bias
      mkt: 'zh-CN' // Force Chinese market/interface (important for Chinese queries)
    }

    const response = await this.fetch(url, {
      method: 'GET',
      query: params,
      signal
    })

    return response
  }

  extractItems(html) {
    const dom = parse(html)
    const resultNodes = dom.querySelectorAll('#b_results > li.b_algo')
    const items = []

    const maxResults = this.maxResults || 10
    for (let i = 0; i < Math.min(resultNodes.length, maxResults); i++) {
      const node = resultNodes[i]

      const titleLink = node.querySelector('h2 > a')
      if (!titleLink) continue

      let link = titleLink.getAttribute('href') || ''
      const title = titleLink.textContent.trim() || ''

      if (!link || !title) continue

      // Keep original Bing URL (tracking link)
      // Decoding is complex and not necessary for search preview

      const snippetNode = node.querySelector('p[class^="b_lineclamp"]')
      const snippet = snippetNode?.textContent?.trim() || ''

      items.push({
        title,
        link,
        snippet,
        rawContent: null
      })
    }

    return items
  }
}
