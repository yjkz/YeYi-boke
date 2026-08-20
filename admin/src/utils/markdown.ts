import DOMPurify from 'dompurify'
import MarkdownIt from 'markdown-it'
import markdownItFootnote from 'markdown-it-footnote'
import markdownItKatex from 'markdown-it-katex'
import Prism from 'prismjs'
import 'katex/dist/katex.min.css'
import 'prismjs/components/prism-bash'
import 'prismjs/components/prism-json'
import 'prismjs/components/prism-python'
import 'prismjs/components/prism-typescript'

const escapeHtml = (value: string) => value
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#039;')

const markdown = new MarkdownIt('commonmark', {
  html: true,
  typographer: true,
  highlight: (code, language) => {
    const name = language.trim().split(/\s+/, 1)[0]
    const grammar = name && Prism.languages[name]
    const highlighted = grammar
      ? Prism.highlight(code, grammar, name)
      : escapeHtml(code)
    const className = name ? ` class="language-${escapeHtml(name)}"` : ''
    return `<pre><code${className}>${highlighted}</code></pre>`
  },
})
markdown.enable(['table', 'strikethrough'])
markdown.use(markdownItFootnote)
  .use(markdownItKatex)

markdown.renderer.rules.math_inline = (tokens, index) => {
  const tex = escapeHtml(tokens[index].content)
  return `<span class="math inline"><span data-tex="${tex}" data-display="false"></span></span>`
}
markdown.renderer.rules.math_block = (tokens, index) => {
  const tex = escapeHtml(tokens[index].content)
  return `<div class="math block"><span data-tex="${tex}" data-display="true"></span></div>\n`
}

const purifierConfig = {
  ADD_ATTR: ['data-tex', 'data-display', 'target', 'rel'],
  ADD_TAGS: ['math', 'semantics', 'mrow', 'mi', 'mo', 'mn', 'msup', 'annotation'],
  ALLOW_DATA_ATTR: false,
  ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto):|\/|#|\.?\/)/i,
}

export const renderMarkdown = (source: string) => DOMPurify.sanitize(markdown.render(source), purifierConfig)
