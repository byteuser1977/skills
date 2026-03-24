import { tool } from './src/index.js'

const args = {
  query: '"北京大学" "理工科" "招生人数" 2024 2023',
  count: 15,
  providers: ['bing']
}

const result = await tool.execute(args)
console.log(JSON.stringify(result, null, 2))
