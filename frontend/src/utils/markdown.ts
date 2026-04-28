import MarkdownIt from 'markdown-it'
import footnote from 'markdown-it-footnote'
import hljs from 'highlight.js/lib/core'

// 按需注册常用语言（控制包体积）
import python from 'highlight.js/lib/languages/python'
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import css from 'highlight.js/lib/languages/css'
import bash from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import xml from 'highlight.js/lib/languages/xml'
import sql from 'highlight.js/lib/languages/sql'

hljs.registerLanguage('python', python)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('css', css)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('shell', bash)
hljs.registerLanguage('json', json)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('sql', sql)

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

const slugify = (s: string) =>
  encodeURIComponent(String(s).trim().toLowerCase().replace(/\s+/g, '-'))

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight(str: string, lang: string) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        const result = hljs.highlight(str, { language: lang, ignoreIllegals: true })
        return `<pre class="hljs-pre"><code class="hljs language-${lang}">${result.value}</code></pre>`
      } catch {
        // 降级到普通代码块渲染
      }
    }

    return `<pre class="hljs-pre"><code class="hljs">${escapeHtml(str)}</code></pre>`
  },
})

// Footnotes support: enables [^1] and [^1]: footnote text syntax
md.use(footnote)

// Add IDs to headings for TOC linking
const originalHeadingOpen = md.renderer.rules.heading_open
md.renderer.rules.heading_open = function (tokens: any, idx: number, options: any, env: any, self: any) {
  const token = tokens[idx]
  if (token.tag === 'h2' || token.tag === 'h3' || token.tag === 'h4') {
    const nextToken = tokens[idx + 1]
    if (nextToken && nextToken.content) {
      token.attrSet('id', slugify(nextToken.content))
    }
  }
  if (originalHeadingOpen) {
    return originalHeadingOpen(tokens, idx, options, env, self)
  }
  return self.renderToken(tokens, idx, options)
}

export function renderMarkdown(source: string): string {
  return md.render(source)
}
