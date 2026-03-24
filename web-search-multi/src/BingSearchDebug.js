/**
 * Bing Search Provider - Debug version
 * Shows what Bing actually returns
 */
import { BaseSearch } from './base.js'
import { parse } from 'node-html-parser'

export class BingSearchDebug extends BaseSearch {
  async executeSearch(query, signal) {
    const html = await this.fetchSerp(query, signal)

    // Save to file for debugging
    const fs = await import('fs')
    fs.writeFileSync('bing-debug.html', html, 'utf8')
    console.error('Saved Bing response to bing-debug.html (length: ' + html.length + ')')

    const items = this.extractItems(html)
    return { items }
  }

  async fetchSerp(query, signal) {
    const url = 'https://www.bing.com/search'
    const params = {
      q: query,
      form: 'QBLH',
      sp: '-1',
      setlang: 'zh-CN',
      cc: 'cn'
    }

    const response = await this.fetch(url, {
      method: 'GET',
      query: params,
      signal,
      headers: {
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    })

    return response
  }

  extractItems(html) {
    const dom = parse(html)

    // Check if we got a CAPTCHA or error page
    const title = dom.querySelector('title')?.textContent || ''
    if (title.includes('CAPTCHA') || html.includes('symptom')) {
      console.error('Bing returned an error page or CAPTCHA')
      console.error('Page title:', title)
      return []
    }

    // Try different selectors
    const selectors = [
      '#b_results > li.b_algo',
      '.b_algo',
      'li[class*="algo"]',
      '.result'
    ]

    let nodes = []
    for (const sel of selectors) {
      const found = dom.querySelectorAll(sel)
      if (found.length > 0) {
        console.error(`Found ${found.length} results using selector: ${sel}`)
        nodes = Array.from(found)
        break
      }
    }

    if (nodes.length === 0) {
      console.error('No results found with any selector')
      console.error('First 1000 chars of HTML:', html.substring(0, 1000))
      return []
    }

    const items = []
    for (let i = 0; i < Math.min(nodes.length, 10); i++) {
      const node = nodes[i]

      const titleLink = node.querySelector('h2 > a, h3 > a, a')
      if (!titleLink) continue

      let link = titleLink.getAttribute('href') || ''
      const title = titleLink.textContent.trim() || ''

      if (!link || !title) continue

      const snippetNode = node.querySelector('p[class^="b_lineclamp"], .b_lineclamp, p')
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
