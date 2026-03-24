import { tool } from './src/index.js'

const args = {
  query: '"2026高考新规一览表"',
  count: 10,
  providers: ['bing']
}

const result = await tool.execute(args)
console.log(JSON.stringify(result, null, 2))
