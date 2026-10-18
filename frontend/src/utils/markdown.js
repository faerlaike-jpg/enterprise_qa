/**
 * Markdown 渲染工具
 * 使用 markdown-it 渲染，highlight.js 实现代码高亮，并为代码块添加语言标签与复制按钮
 */
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js/lib/common'

const md = new MarkdownIt({
  html: false, // 禁止原始 HTML，防止 XSS
  linkify: true,
  breaks: true,
  highlight(code, lang) {
    const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext'
    const html = hljs.highlight(code, { language, ignoreIllegals: true }).value
    return (
      `<pre class="code-block"><div class="code-head"><span>${language}</span>` +
      `<button class="copy-btn" data-copy>复制</button></div>` +
      `<code class="hljs language-${language}">${html}</code></pre>`
    )
  },
})

// 链接在新窗口打开
const defaultLinkOpen =
  md.renderer.rules.link_open || ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options))
md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  tokens[idx].attrSet('target', '_blank')
  tokens[idx].attrSet('rel', 'noopener noreferrer')
  return defaultLinkOpen(tokens, idx, options, env, self)
}

/**
 * 将 Markdown 文本渲染为 HTML
 * @param {string} text Markdown 文本
 * @returns {string} HTML 字符串
 */
export function renderMarkdown(text) {
  return md.render(text || '')
}

/**
 * 代码块复制按钮的事件委托处理，在消息容器上监听 click 即可
 * @param {MouseEvent} e 点击事件
 */
export function handleCopyClick(e) {
  const btn = e.target.closest('[data-copy]')
  if (!btn) return
  const code = btn.closest('pre')?.querySelector('code')?.innerText || ''
  navigator.clipboard.writeText(code).then(() => {
    btn.textContent = '已复制'
    setTimeout(() => (btn.textContent = '复制'), 1500)
  })
}
