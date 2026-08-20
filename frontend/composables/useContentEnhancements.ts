import DOMPurify from 'isomorphic-dompurify'
import katex from 'katex'
import Prism from 'prismjs'

import 'katex/dist/katex.min.css'
import 'prismjs/components/prism-bash'
import 'prismjs/components/prism-json'
import 'prismjs/components/prism-python'
import 'prismjs/components/prism-typescript'

const purifierConfig = {
  ADD_ATTR: ['data-tex', 'data-display', 'target', 'rel'],
  ADD_TAGS: ['math', 'semantics', 'mrow', 'mi', 'mo', 'mn', 'msup', 'annotation'],
  ALLOW_DATA_ATTR: false,
  ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto):|\/|#|\.?\/)/i,
}

export const sanitizeContentHtml = (html: string) => DOMPurify.sanitize(html, purifierConfig)

export const enhanceContent = (root: HTMLElement | null) => {
  if (!root) return

  root.querySelectorAll<HTMLElement>('pre code[class*="language-"]').forEach((element) => {
    Prism.highlightElement(element)
  })

  root.querySelectorAll<HTMLElement>('[data-tex]').forEach((element) => {
    const tex = element.dataset.tex
    if (!tex) return
    katex.render(tex, element, {
      displayMode: element.dataset.display === 'true',
      throwOnError: false,
      output: 'htmlAndMathml',
    })
  })
}
