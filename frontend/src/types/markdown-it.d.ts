declare module 'markdown-it' {
  export interface MarkdownItOptions {
    html?: boolean
    xhtmlOut?: boolean
    breaks?: boolean
    langPrefix?: string
    linkify?: boolean
    typographer?: boolean
    quotes?: string
    highlight?: (str: string, lang: string) => string
  }

  export interface Token {
    type: string
    tag: string
    attrs: [string, string][]
    content: string
    attrSet(name: string, value: string): void
    attrPush(attr: [string, string]): void
  }

  export interface Renderer {
    rules: Record<string, any>
    render(tokens: Token[], options: any, env: any): string
    renderToken(tokens: Token[], idx: number, options: any): string
  }

  export interface MarkdownItUtils {
    escapeHtml(str: string): string
  }

  export default class MarkdownIt {
    constructor(options?: MarkdownItOptions)
    render(src: string): string
    use(plugin: any, ...params: any[]): this
    utils: MarkdownItUtils
    renderer: Renderer
  }
}
