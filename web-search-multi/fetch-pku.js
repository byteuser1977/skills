import { fetch } from 'undici'
import { parse } from 'node-html-parser'

const url = 'https://admissions.pku.edu.cn/zsxx1/index.htm' // 北大本科招生网

try {
  console.error(`Fetching: ${url}`)
  const res = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    },
    redirect: 'follow'
  })

  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const html = await res.text()
  console.error(`HTML length: ${html.length}`)

  const dom = parse(html)

  // 简单查找页面上的数字年份（2022 2023 2024）和“招生”“人数”等词
  const text = dom.textContent
  const matches = []

  // 查找包含年份和数字的行
  const lines = text.split(/\n|\r|\u2028|\u2029/)
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue
    // 检查是否包含 2022|2023|2024 和 数字（可能是招生人数）
    if (/(2022|2023|2024)/.test(trimmed) && /\d+/.test(trimmed) && /招生|计划|录取|人数/.test(trimmed)) {
      matches.push(trimmed)
    }
  }

  console.log('=== 可能的招生数据行 ===')
  matches.slice(0, 20).forEach((m, i) => console.log(`${i + 1}. ${m}`))

  // 统计 mention of "理工"
  const sciEng = text.match(/理工/g) || []
  console.log(`\n理工 mentions: ${sciEng.length}`)

  process.exit(0)
} catch (err) {
  console.error('Error:', err.message)
  process.exit(1)
}
