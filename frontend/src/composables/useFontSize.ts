import { ref, watch, onMounted } from 'vue'

const STORAGE_KEY = 'blog-font-scale'
const MIN = 0.85
const MAX = 1.35
const STEP = 0.05

export function useFontSize() {
  const scale = ref(1)

  function applyScale() {
    document.documentElement.style.setProperty('--article-font-scale', String(scale.value))
  }

  function increase() {
    scale.value = Math.min(MAX, Math.round((scale.value + STEP) * 100) / 100)
  }

  function decrease() {
    scale.value = Math.max(MIN, Math.round((scale.value - STEP) * 100) / 100)
  }

  function reset() {
    scale.value = 1
  }

  onMounted(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const v = parseFloat(stored)
      if (!isNaN(v) && v >= MIN && v <= MAX) scale.value = v
    }
    applyScale()
  })

  watch(scale, (v) => {
    localStorage.setItem(STORAGE_KEY, String(v))
    applyScale()
  })

  return { scale, increase, decrease, reset }
}
