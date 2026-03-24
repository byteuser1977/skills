/**
 * DuckDuckGo Search Provider
 * Based on Chatbox's duckduckgo.ts
 */
import { BaseSearch } from './base.js'
import { parse } from 'node-html-parser'

export class DuckDuckGoSearch extends BaseSearch {
  async executeSearch(query, signal) {
    const html = await this.fetchSerp(query, signal)
    const items = this.extractItems(html)
    return { items }
  }

  async fetchSerp(query, signal) {
    const url = 'https://html.duckduckgo.com/html/'
    const body = new URLSearchParams({
      q: query,
      df: 'y' // Date range: past year
    })

    const response = await this.fetch(url, {
      method: 'POST',
      body: body.toString(),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      signal
    })

    return response
  }

  extractItems(html) {
    const dom = parse(html)
    const resultNodes = dom.querySelectorAll('.results_links')
    const items = []

    for (let i = 0; i < Math.min(resultNodes.length, 10); i++) {
      const node = resultNodes[i]

      const titleLink = node.querySelector('.result__a')
      if (!titleLink) continue

      const link = titleLink.getAttribute('href') || ''
      const title = titleLink.textContent.trim() || ''

      if (!link || !title) continue

      const snippetNode = node.querySelector('.result__snippet')
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
