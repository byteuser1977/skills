#!/usr/bin/env node

/**
 * OpenClaw Skill Wrapper: web-search-multi
 *
 * Reads JSON from stdin or command line argument,
 * executes the tool, outputs JSON result.
 */

import { tool } from '../src/index.js'

async function main() {
  // Read input from CLI arg or stdin
  let input = process.argv[2]

  if (!input && !process.stdin.isTTY) {
    input = await new Promise(resolve => {
      let data = ''
      process.stdin.on('data', chunk => data += chunk)
      process.stdin.on('end', () => resolve(data.trim()))
    })
  }

  if (!input) {
    console.error(JSON.stringify({
      error: 'Missing input. Provide JSON with "query" field.'
    }))
    process.exit(1)
  }

  let args
  try {
    args = JSON.parse(input)
  } catch (e) {
    console.error(JSON.stringify({
      error: 'Invalid JSON input: ' + e.message
    }))
    process.exit(1)
  }

  // Setup abort signal for cancellation
  const controller = new AbortController()
  const signalHandler = () => controller.abort()
  process.on('SIGTERM', signalHandler)
  process.on('SIGINT', signalHandler)

  try {
    const result = await tool.execute(args, controller.signal)
    console.log(JSON.stringify(result))
  } catch (error) {
    console.error(JSON.stringify({
      error: error.message,
      code: error.code || 'EXECUTION_ERROR'
    }))
    process.exit(1)
  } finally {
    process.removeListener('SIGTERM', signalHandler)
    process.removeListener('SIGINT', signalHandler)
  }
}

main().catch(err => {
  console.error(JSON.stringify({
    error: 'Unhandled error: ' + err.message
  }))
  process.exit(1)
})
