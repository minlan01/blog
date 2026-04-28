import { watch } from 'vue'
import { useRoute } from 'vue-router'

interface SeoParams {
  title?: string
  description?: string
  image?: string
  url?: string
  type?: string
}

const SITE_NAME = 'minlan01'
const DEFAULT_DESCRIPTION = '一个技术博客'
const DEFAULT_IMAGE = '/og-image.png'

function setMeta(attr: string, key: string, content: string) {
  let el = document.querySelector(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

export function useSeo(params: SeoParams = {}) {
  const route = useRoute()
  const baseUrl = window.location.origin

  const title = params.title ? `${params.title} — ${SITE_NAME}` : SITE_NAME
  const description = params.description || DEFAULT_DESCRIPTION
  const image = params.image || DEFAULT_IMAGE
  const url = params.url || `${baseUrl}${route.path}`
  const type = params.type || 'website'

  document.title = title

  // Standard meta
  setMeta('name', 'description', description)

  // Open Graph
  setMeta('property', 'og:title', title)
  setMeta('property', 'og:description', description)
  setMeta('property', 'og:image', image)
  setMeta('property', 'og:url', url)
  setMeta('property', 'og:type', type)
  setMeta('property', 'og:site_name', SITE_NAME)

  // Twitter Card
  setMeta('name', 'twitter:card', 'summary_large_image')
  setMeta('name', 'twitter:title', title)
  setMeta('name', 'twitter:description', description)
  setMeta('name', 'twitter:image', image)
}

export function usePageSeo() {
  const route = useRoute()

  watch(
    () => route.path,
    () => {
      const meta = route.meta as Record<string, any>
      useSeo({
        title: meta.title as string | undefined,
      })
    },
    { immediate: true }
  )
}
