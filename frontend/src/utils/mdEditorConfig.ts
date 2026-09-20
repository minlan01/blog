import { config } from 'md-editor-v3'
import { ref } from 'vue'

const UNPKG = '/unpkg'

const narrowQuery = window.matchMedia('(max-width: 767px)')
export const isNarrowScreen = ref(narrowQuery.matches)
narrowQuery.addEventListener('change', (e) => {
  isNarrowScreen.value = e.matches
})

let initialized = false

// md-editor-v3 的扩展模块默认运行时从 unpkg.com 懒加载，国内直连不可靠；
// 统一改走同源 /unpkg/（nginx 反代到 unpkg.com），由服务器侧获取。
export function setupMdEditorExtensions(): void {
  if (initialized) return
  initialized = true
  config({
    editorExtensions: {
      highlight: {
        js: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/highlight.min.js`,
        css: {
          a11y: {
            light: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/a11y-light.min.css`,
            dark: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/a11y-dark.min.css`,
          },
          atom: {
            light: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/atom-one-light.min.css`,
            dark: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/atom-one-dark.min.css`,
          },
          github: {
            light: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/github.min.css`,
            dark: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/github-dark.min.css`,
          },
          gradient: {
            light: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/gradient-light.min.css`,
            dark: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/gradient-dark.min.css`,
          },
          kimbie: {
            light: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/kimbie-light.min.css`,
            dark: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/kimbie-dark.min.css`,
          },
          paraiso: {
            light: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/paraiso-light.min.css`,
            dark: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/paraiso-dark.min.css`,
          },
          qtcreator: {
            light: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/qtcreator-light.min.css`,
            dark: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/qtcreator-dark.min.css`,
          },
          stackoverflow: {
            light: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/stackoverflow-light.min.css`,
            dark: `${UNPKG}/@highlightjs/cdn-assets@11.11.1/styles/stackoverflow-dark.min.css`,
          },
        },
      },
      prettier: {
        standaloneJs: `${UNPKG}/prettier@3.8.1/standalone.js`,
        parserMarkdownJs: `${UNPKG}/prettier@3.8.1/plugins/markdown.js`,
      },
      cropper: {
        js: `${UNPKG}/cropperjs@1.6.2/dist/cropper.min.js`,
        css: `${UNPKG}/cropperjs@1.6.2/dist/cropper.min.css`,
      },
      screenfull: { js: `${UNPKG}/screenfull@5.2.0/dist/screenfull.js` },
      mermaid: { js: `${UNPKG}/mermaid@11.12.3/dist/mermaid.min.js` },
      katex: {
        js: `${UNPKG}/katex@0.16.33/dist/katex.min.js`,
        css: `${UNPKG}/katex@0.16.33/dist/katex.min.css`,
      },
      echarts: { js: `${UNPKG}/echarts@6.0.0/dist/echarts.min.js` },
    },
  })
}
