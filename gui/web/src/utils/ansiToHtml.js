/**
 * 将 ANSI 颜色代码转换为 HTML
 * @param {string} text - 包含 ANSI 代码的文本
 * @returns {string} - 转换后的 HTML 字符串
 */
export function ansiToHtml(text) {
  if (!text) return ''

  const ansiMap = {
    '\x1b[30m': '<span style="color:#000000">',
    '\x1b[31m': '<span style="color:#ff0000">',
    '\x1b[32m': '<span style="color:#00ff00">',
    '\x1b[33m': '<span style="color:#ffaa00">',
    '\x1b[34m': '<span style="color:#0000ff">',
    '\x1b[35m': '<span style="color:#ff00ff">',
    '\x1b[36m': '<span style="color:#00ffff">',
    '\x1b[37m': '<span style="color:#aaaaaa">',
    '\x1b[1m': '<span style="font-weight:bold">',
    '\x1b[4m': '<span style="text-decoration:underline">',
    '\x1b[7m': '<span style="background:#555555">',
    '\x1b[40m': '<span style="background:#000000">',
    '\x1b[41m': '<span style="background:#ff0000">',
    '\x1b[42m': '<span style="background:#00ff00">',
    '\x1b[43m': '<span style="background:#ffaa00">',
    '\x1b[44m': '<span style="background:#0000ff">',
    '\x1b[45m': '<span style="background:#ff00ff">',
    '\x1b[46m': '<span style="background:#00ffff">',
    '\x1b[47m': '<span style="background:#aaaaaa">',
    '\x1b[0m': '</span>',
    '\x1b[m': '</span>',
  }

  let result = text

  // 替换已知的 ANSI 代码
  for (const [code, html] of Object.entries(ansiMap)) {
    result = result.replaceAll(code, html)
  }

  // 移除其他未处理的 ANSI 代码
  result = result.replace(/\x1b\[[0-9;]*m/g, '')

  // 将换行符转换为 <br>
  result = result.replace(/\n/g, '<br>')

  return result
}