import { onMounted, onUnmounted, ref, type Ref } from 'vue'

/**
 * 滚动渐入动画 composable
 * 使用 IntersectionObserver 监听元素进入视口
 */
export function useScrollReveal(
  threshold = 0.15,
  rootMargin = '0px 0px -40px 0px'
) {
  const targets: Set<Element> = new Set()
  let observer: IntersectionObserver | null = null

  onMounted(() => {
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed')
            observer?.unobserve(entry.target)
          }
        })
      },
      { threshold, rootMargin }
    )

    targets.forEach((el) => observer?.observe(el))
  })

  onUnmounted(() => {
    observer?.disconnect()
  })

  /** 返回一个 ref callback 用于 v-ref 绑定 */
  function reveal(el: Element | null) {
    if (!el) return
    targets.add(el)
    observer?.observe(el)
  }

  return { reveal }
}

/**
 * 简化版：给单个元素使用
 * 返回一个 ref 和一个 visible 状态
 */
export function useInView(threshold = 0.15) {
  const target = ref<HTMLElement | null>(null) as Ref<HTMLElement | null>
  const visible = ref(false)
  let observer: IntersectionObserver | null = null

  onMounted(() => {
    if (!target.value) return
    observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          visible.value = true
          observer?.disconnect()
        }
      },
      { threshold }
    )
    observer.observe(target.value)
  })

  onUnmounted(() => {
    observer?.disconnect()
  })

  return { target, visible }
}
