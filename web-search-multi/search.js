import { tool } from './src/index.js'
import { writeFileSync } from 'fs'

const args = {
  query: '"2026高考新规一览表" site:gaokao.com',  // search exact title
  count: 10,
  providers: ['bing']  // use only Bing to avoid Sogou redirects
}

console.error('Searching...')
const result = await tool.execute(args)
const output = JSON.stringify(result, null, 2)
writeFileSync('tmp/gaokao-2026.json', output, 'utf8')
console.log(output)
