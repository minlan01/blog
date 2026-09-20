import { onMounted, onUnmounted, type Ref } from 'vue'

/**
 * 磁吸按钮效果 — 鼠标靠近时元素被吸引偏移
 * 用法：const el = ref<HTMLElement | null>(null); useMagnetic(el)
 */
export function useMagnetic(el: Ref<HTMLElement | null>, strength = 0.3) {
  let rafId = 0

  function onMove(e: MouseEvent) {
    if (!el.value) return
    const rect = el.value.getBoundingClientRect()
    const cx = rect.left + rect.width / 2
    const cy = rect.top + rect.height / 2
    const dx = (e.clientX - cx) * strength
    const dy = (e.clientY - cy) * strength
    cancelAnimationFrame(rafId)
    rafId = requestAnimationFrame(() => {
      if (el.value) {
        el.value.style.transform = `translate(${dx}px, ${dy}px)`
      }
    })
  }

  function onLeave() {
    if (!el.value) return
    cancelAnimationFrame(rafId)
    el.value.style.transform = ''
    el.value.style.transition = 'transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)'
    setTimeout(() => {
      if (el.value) el.value.style.transition = ''
    }, 400)
  }

  function onEnter() {
    if (el.value) {
      el.value.style.transition = 'transform 0.1s ease-out'
    }
  }

  onMounted(() => {
    if (!el.value) return
    el.value.addEventListener('mousemove', onMove)
    el.value.addEventListener('mouseenter', onEnter)
    el.value.addEventListener('mouseleave', onLeave)
  })

  onUnmounted(() => {
    if (!el.value) return
    el.value.removeEventListener('mousemove', onMove)
    el.value.removeEventListener('mouseenter', onEnter)
    el.value.removeEventListener('mouseleave', onLeave)
    cancelAnimationFrame(rafId)
  })
}
