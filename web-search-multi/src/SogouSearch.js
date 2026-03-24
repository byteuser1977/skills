/**
 * Sogou Search Provider
 * Based on web_fetch analysis of sogou.com/web
 */
import { BaseSearch } from './base.js'
import { parse } from 'node-html-parser'

export class SogouSearch extends BaseSearch {
  constructor(options = {}) {
    super()
    this.maxResults = options.maxResults || 10
  }

  async executeSearch(query, signal) {
    const html = await this.fetchSerp(query, signal)
    const items = this.extractItems(html)
    return { items }
  }

  async fetchSerp(query, signal) {
    const url = 'https://www.sogou.com/web'
    const params = {
      query: query,
      ie: 'utf8' // Ensure UTF-8 encoding
    }

    // Sogou may need specific headers to appear as browser
    const response = await this.fetch(url, {
      method: 'GET',
      query: params,
      signal,
      headers: {
        // Sogou-specific headers
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.sogou.com/'
      }
    })

    return response
  }

  extractItems(html) {
    const dom = parse(html)

    // Check for CAPTCHA or error
    const title = dom.querySelector('title')?.textContent || ''
    if (title.includes('登录') || html.includes('验证码') || html.includes('captcha')) {
      console.error('Sogou returned login/captcha page')
      return []
    }

    // Sogou result selectors
    // Primary: .vrwrap (verified from actual HTML)
    // Fallback: [class*="result"], h3 parents
    let resultNodes = []
    const primarySelector = '.vrwrap'
    let nodes = dom.querySelectorAll(primarySelector)
    if (nodes.length > 0) {
      console.error(`Found ${nodes.length} results using primary selector: ${primarySelector}`)
      resultNodes = Array.from(nodes)
    } else {
      // Fallback: look for any element with class containing "result"
      const fallback = dom.querySelectorAll('[class*="result"]')
      if (fallback.length > 0) {
        console.error(`Fallback: found ${fallback.length} elements with [class*="result"]`)
        resultNodes = Array.from(fallback)
      } else {
        // Last resort: use h3 parents
        const allH3 = dom.querySelectorAll('h3')
        resultNodes = Array.from(allH3).map(h3 => h3.parentElement).filter(p => p)
        console.error(`Last resort: found ${resultNodes.length} h3 parents`)
      }
    }

    const items = []
    const maxResults = this.maxResults || 10
    for (let i = 0; i < Math.min(resultNodes.length, maxResults); i++) {
      const node = resultNodes[i]

      // Find title and link: look for <a> within h3 or any prominent link
      const titleLink = node.querySelector('h3 a') || node.querySelector('h2 a') || node.querySelector('a')
      if (!titleLink) continue

      let link = titleLink.getAttribute('href') || ''
      const title = titleLink.textContent.trim() || ''

      if (!title) continue

      // Sogou uses redirect links like /link?url=...
      // Need to resolve to actual URL
      link = this.resolveSogouUrl(link)

      // Find snippet/description
      const snippetNode = node.querySelector('p.str, p, .str, .snippet, .content')
      const snippet = snippetNode?.textContent?.trim() || ''

      // Find date/time if available
      // const timeNode = node.querySelector('.time, .date, time')
      // const time = timeNode?.textContent?.trim() || ''

      if (link) {
        items.push({
          title,
          link,
          snippet,
          rawContent: null
        })
      }
    }

    return items
  }

  /**
   * Resolve Sogou redirect URL to actual destination
   * Sogou uses various redirect formats:
   * - /link?url=<encoded_url> (standard)
   * - /link?url=<short_hash> (encoded hash)
   * - ?query=params (search hint links)
   * - <short_code> (no prefix)
   */
  
  resolveSogouUrl(url) {
    if (!url) return ''

    // Already absolute URL (http/https)
    if (/^https?:\/\//i.test(url)) {
      return url
    }

    try {
      // Case 1: Sogou redirect /link?url=<code>
      // Keep the full redirect URL, prepend base domain
      if (url.includes('/link?url=')) {
        return 'https://www.sogou.com' + url
      }

      // Case 2: Search suggestion links (skip)
      if (url.startsWith('?') && url.includes('query=')) {
        return ''
      }

      // Case 3: Relative path starting with /
      if (url.startsWith('/')) {
        return 'https://www.sogou.com' + url
      }

      // Case 4: Bare short code (looks like base64-like, long alphanumeric)
      // This happens due to malformed extraction. Wrap it as redirect.
      if (/^[a-zA-Z0-9_-]{20,}$/.test(url)) {
        return 'https://www.sogou.com/link?url=' + url
      }
    } catch (e) {
      // ignore errors
    }

    // Unknown format, skip
    return ''
  }
esolveSogouUrl(url) {
    if (!url) return ''

    // If already absolute URL (starts with http/https/mailto), return as-is
    if (/^https?:\/\//i.test(url) || url.startsWith('mailto:') || url.startsWith('javascript:')) {
      return url.startsWith('http') ? url : '' // Skip non-http(s) links
    }

    try {
      // Case 1: Full redirect with /link?url=
      if (url.includes('/link?url=')) {
        const base = url.startsWith('http') ? '' : 'https://www.sogou.com'
        const urlObj = new URL(url, base)
        const encoded = urlObj.searchParams.get('url')
        if (encoded) {
          try {
            // Try decode once
            return decodeURIComponent(encoded)
          } catch (e) {
            // If it's a short hash, it may not be decodable
            // In that case, return as-is (it's a Sogou internal link)
            return 'https://www.sogou.com' + url.split('?')[0]
          }
        }
      }

      // Case 2: Query parameters only (hint links) - skip these
      if (url.startsWith('?') && url.includes('query=')) {
        return '' // These are suggestion links, not results
      }

      // Case 3: Relative path starting with /
      if (url.startsWith('/')) {
        return 'https://www.sogou.com' + url
      }

      // Case 4: Short code without prefix (e.g., hedJjaC291...)
      // These are Sogou's short redirect links, need to prepend /link?url=?
      // Actually they appear as href="hedJjaC291..." which is malformed
      // Likely it's part of the /link?url= value but extracted incorrectly
      // We'll skip these as they are useless without proper resolution
    } catch (e) {
      // ignore parsing errors
    }

    // For unknown formats, return empty to skip
    return ''
  }
}
