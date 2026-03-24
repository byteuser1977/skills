/**
 * Truncate text to a maximum length with ellipsis
 * Based on lodash.truncate
 *
 * @param {string} text - Input text
 * @param {Object} options - { length: number, separator?: string }
 * @returns {string}
 */
export function truncate(text, { length = 150, separator = '' } = {}) {
  if (!text || text.length <= length) {
    return text
  }

  const subString = text.substring(0, length)
  const words = subString.split(separator || ' ')

  // If last word is incomplete, remove it
  if (words.length > 1 && words[words.length - 1].length > 0) {
    words.pop()
  }

  let truncated = words.join(separator || ' ')
  if (truncated.length < text.length) {
    truncated += '...'
  }

  return truncated
}
