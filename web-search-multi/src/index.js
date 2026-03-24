/**
 * OpenClaw Skill: web-search-multi
 *
 * Multi-provider web search with parallel execution and round-robin merging.
 * Based on Chatbox's web-search implementation.
 */

import { MultiSearch } from './MultiSearch.js'
import { BingSearch } from './BingSearch.js'
import { SogouSearch } from './SogouSearch.js'
import { TavilySearch } from './TavilySearch.js'
import { MemoryCache } from './MemoryCache.js'

/**
 * Tool definition for OpenClaw
 */
export const tool = {
  name: 'web_search_multi',
  description: 'Search the web using multiple providers (Bing, DuckDuckGo, Tavily) with parallel execution. Returns current information from the internet with balanced results from different sources.',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'The search query. Be specific and concise.'
      },
      count: {
        type: 'number',
        description: 'Number of search results to return (between 1 and 20). Default is 10.',
        default: 10,
        minimum: 1,
        maximum: 20
      },
      providers: {
        type: 'array',
        items: {
          type: 'string',
          enum: ['bing', 'sogou', 'tavily']
        },
        description: 'List of search providers to use. Default: ["bing"]'
      }
    },
    required: ['query']
  },

  /**
   * Execute the tool
   * @param {Object} args - Tool arguments
   * @param {string} args.query - Search query
   * @param {number} [args.count] - Number of results
   * @param {Array<string>} [args.providers] - Provider list
   * @param {AbortSignal} signal - Cancellation signal
   * @returns {Promise<Object>} Search results
   */
  execute: async function(args, signal) {
    const { query, count = 10, providers = ['bing'] } = args
    const maxResults = Math.min(Math.max(1, count), 20)

    // Build provider instances
    const providerInstances = []
    const config = await loadConfig()

    for (const p of providers) {
      switch (p) {
        case 'bing':
          providerInstances.push(new BingSearch())
          break
        case 'sogou':
          providerInstances.push(new SogouSearch({
            maxResults: config.sogou?.maxResults || 10
          }))
          break
        case 'tavily':
          if (config.tavily?.apiKey) {
            providerInstances.push(new TavilySearch({
              apiKey: config.tavily.apiKey,
              searchDepth: config.tavily.searchDepth || 'basic',
              maxResults: config.tavily.maxResults || 5,
              timeRange: config.tavily.timeRange,
              includeRawContent: config.tavily.includeRawContent
            }))
          } else {
            console.warn('Tavily provider skipped: no API key configured')
          }
          break
        default:
          console.warn(`Unknown provider: ${p}, skipping`)
      }
    }

    if (providerInstances.length === 0) {
      throw new Error('No providers available. Configure at least one search provider.')
    }

    const cache = new MemoryCache(5 * 60 * 1000) // 5 min TTL
    const multi = new MultiSearch(providerInstances, {
      maxResults,
      cache,
      snippetLength: 150
    })

    const startTime = Date.now()
    const items = await multi.search(query, signal)
    const duration = Date.now() - startTime

    return {
      query,
      searchResults: items,
      total: items.length,
      providers: providerInstances.map(p => p.constructor.name.replace('Search', '').toLowerCase()),
      duration,
      timestamp: Date.now()
    }
  }
}

/**
 * Load configuration from config file or environment
 * @private
 */
async function loadConfig() {
  try {
    // Try to load config.json from skill directory
    const configPath = './config.json'
    // Use dynamic import for ESM
    // Since we're in a skill context, config might be passed differently
    // For now, read from environment variables
    return {
      tavily: {
        apiKey: process.env.TAVILY_API_KEY || null
      }
    }
  } catch (e) {
    return { tavily: {} }
  }
}

// Standalone test
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv[2]
    ? JSON.parse(process.argv[2])
    : { query: 'OpenClaw AI', count: 5 }

  tool.execute(args)
    .then(result => {
      console.log(JSON.stringify(result, null, 2))
    })
    .catch(err => {
      console.error('Error:', err.message)
      process.exit(1)
    })
}

export default { tool }
