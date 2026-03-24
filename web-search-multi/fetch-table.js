import { fetch } from 'undici'
import { parse } from 'node-html-parser'

const url = 'http://mp.weixin.qq.com/s?src=11&timestamp=1773666470&ver=6602&signature=LSCjYAXbnT1shWftSQUjkVOD4pnSVKIebhZsH5iYuHl2eu28YxFjVYgri7-gO4SqUSzcT6Mw-dY1l3vZYs3Q7hhvgAhkmQwxS36hfJM-NVH9DGCLvBlgk*5tm3WYZlTd&new=1'

try {
  console.error(`Fetching: ${url}`)
  const res = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    },
    redirect: 'follow' // follow redirects through Sogou
  })

  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const html = await res.text()

  console.error(`HTML length: ${html.length}`)

  // Parse HTML
  const dom = parse(html)

  // Strategy: Find table containing "2026高考新规"
  // Remove scripts and styles
  const body = dom.querySelector('body')
  if (!body) throw new Error('No body found')

  // Find all tables
  const tables = body.querySelectorAll('table')
  console.error(`Found ${tables.length} tables`)

  // Look for table with keyword
  let targetTable = null
  for (const tbl of tables) {
    const text = tbl.textContent
    if (text.includes('2026') && text.includes('高考') && text.includes('新规')) {
      targetTable = tbl
      break
    }
  }

  if (!targetTable) {
    // Fallback: Find h1/h2 with title and adjacent table
    const headers = body.querySelectorAll('h1, h2, h3')
    for (const h of headers) {
      if (h.textContent.includes('高考新规') || h.textContent.includes('一览表')) {
        // Next sibling might be table or contain table
        let next = h.nextElementSibling
        while (next) {
          if (next.tagName === 'TABLE') {
            targetTable = next
            break
          }
          next = next.nextElementSibling
        }
        if (targetTable) break
      }
    }
  }

  if (!targetTable) {
    // As last resort, dump body text to some extent
    console.error('Target table not found. Dumping first 2000 chars of body:')
    console.error(body.textContent.substring(0, 2000))
    process.exit(1)
  }

  // Extract table into Markdown
  const rows = targetTable.querySelectorAll('tr')
  const markdown = []
  markdown.push('| 序号 | 项目 | 内容 | 备注 |')
  markdown.push('|------|------|------|------|')

  rows.forEach((row, idx) => {
    const cells = row.querySelectorAll('th, td')
    if (cells.length === 0) return

    const texts = Array.from(cells).map(c => c.textContent.trim().replace(/\|/g, '\\|'))
    // Pad to at least 4 columns
    while (texts.length < 4) texts.push('')
    markdown.push(`| ${texts.slice(0, 4).join(' | ')} |`)
  })

  console.log(markdown.join('\n'))
  process.exit(0)
} catch (err) {
  console.error('Fetch error:', err.message)
  process.exit(1)
}
