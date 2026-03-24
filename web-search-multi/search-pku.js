import { tool } from './src/index.js'
import { writeFileSync } from 'fs'

const args = {
  query: '北京大学 2024 2023 2022 理工科 招生人数 录取统计',
  count: 10,
  providers: ['bing', 'sogou']
}

const result = await tool.execute(args)
const output = JSON.stringify(result, null, 2)
writeFileSync('tmp/pku-enrollment.json', output, 'utf8')
console.log(output)
