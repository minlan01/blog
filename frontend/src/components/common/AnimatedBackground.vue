<template>
  <div class="bg" aria-hidden="true">
    <div class="bg__base"></div>
    <div class="bg__glow"></div>
    <canvas ref="canvas" class="bg__rain"></canvas>
    <div class="bg__scanline"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useTheme } from '@/composables/useTheme'

const canvas = ref<HTMLCanvasElement | null>(null)
const { theme } = useTheme()
let animFrame = 0
let resizeHandler: (() => void) | null = null
let visibilityHandler: (() => void) | null = null

const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%&*{}[];:<>?/~'
const FONT_SIZE = 15

// ── 性能决策 ──
// 小屏设备（手机/小平板）或低性能场景直接不启动 Canvas
const isMobile = window.innerWidth < 768 || /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
// 尊重用户系统偏好
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
const enableCanvas = !isMobile && !prefersReducedMotion

function init() {
  if (!canvas.value || !enableCanvas) {
    // 不启动 Canvas，背景仍有渐变光晕和扫描线
    return
  }
  const el: HTMLCanvasElement = canvas.value
  const ctx: CanvasRenderingContext2D = el.getContext('2d', { alpha: true })!

  function resize() {
    el.width = window.innerWidth
    el.height = window.innerHeight
  }
  resize()

  // debounce resize
  let resizeTimer: ReturnType<typeof setTimeout> | null = null
  resizeHandler = () => {
    if (resizeTimer) clearTimeout(resizeTimer)
    resizeTimer = setTimeout(resize, 200)
  }
  window.addEventListener('resize', resizeHandler)

  const columns = Math.floor(el.width / FONT_SIZE)
  const drops: number[] = Array(columns).fill(0).map(() => Math.random() * -100)

  let running = true

  // ── 页面可见性暂停 ──
  visibilityHandler = () => {
    if (document.hidden) {
      running = false
    } else if (!running) {
      running = true
      lastFrame = performance.now()
      animFrame = requestAnimationFrame(draw)
    }
  }
  document.addEventListener('visibilitychange', visibilityHandler)

  // ── 降帧：30fps（每 33ms 一帧），减少 GPU 压力 ──
  const FRAME_INTERVAL = 1000 / 30
  let lastFrame = performance.now()

  function draw(now: number) {
    if (!running) return

    // 节流到 30fps
    if (now - lastFrame < FRAME_INTERVAL) {
      animFrame = requestAnimationFrame(draw)
      return
    }
    lastFrame = now

    const isLight = theme.value === 'light'

    ctx.fillStyle = isLight ? 'rgba(250, 247, 242, 0.05)' : 'rgba(10, 10, 10, 0.05)'
    ctx.fillRect(0, 0, el.width, el.height)

    ctx.font = `${FONT_SIZE}px "JetBrains Mono", monospace`

    for (let i = 0; i < drops.length; i++) {
      const char = CHARS[Math.floor(Math.random() * CHARS.length)]
      const y = drops[i] * FONT_SIZE

      if (isLight) {
        ctx.fillStyle = 'rgba(217, 119, 6, 0.40)'
      } else {
        ctx.fillStyle = 'rgba(0, 255, 65, 0.5)'
      }
      ctx.fillText(char, i * FONT_SIZE, y)

      if (drops[i] > 1) {
        const prevChar = CHARS[Math.floor(Math.random() * CHARS.length)]
        if (isLight) {
          ctx.fillStyle = 'rgba(217, 119, 6, 0.18)'
        } else {
          ctx.fillStyle = 'rgba(0, 255, 65, 0.25)'
        }
        ctx.fillText(prevChar, i * FONT_SIZE, (drops[i] - 1) * FONT_SIZE)
      }

      const resetThreshold = isLight ? 0.97 : 0.975
      if (y > el.height && Math.random() > resetThreshold) {
        drops[i] = 0
      }
      drops[i]++
    }

    animFrame = requestAnimationFrame(draw)
  }

  animFrame = requestAnimationFrame(draw)
}

onMounted(init)

onUnmounted(() => {
  cancelAnimationFrame(animFrame)
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
  if (visibilityHandler) document.removeEventListener('visibilitychange', visibilityHandler)
})
</script>

<style scoped>
.bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
}

.bg__base {
  position: absolute;
  inset: 0;
  background: var(--color-bg-deep);
}

.bg__glow {
  position: absolute;
  inset: 0;
  opacity: 0;
  background:
    radial-gradient(ellipse 60% 50% at 20% 50%, rgba(99, 102, 241, 0.06), transparent),
    radial-gradient(ellipse 50% 60% at 80% 30%, rgba(139, 92, 246, 0.04), transparent);
  pointer-events: none;
  transition: opacity 0.8s ease;
}

[data-theme="light"] .bg__glow {
  opacity: 1;
  background:
    radial-gradient(ellipse 80% 60% at 30% 40%, rgba(217, 119, 6, 0.10), transparent),
    radial-gradient(ellipse 70% 50% at 75% 60%, rgba(245, 158, 11, 0.08), transparent);
}

.bg__rain {
  position: absolute;
  inset: 0;
}

.bg__scanline {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(255, 255, 255, 0.015) 2px,
    rgba(255, 255, 255, 0.015) 4px
  );
  pointer-events: none;
}

[data-theme="light"] .bg__scanline {
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.008) 2px,
    rgba(0, 0, 0, 0.008) 4px
  );
}

@media (max-width: 768px) {
  .bg__rain {
    display: none;
  }
  .bg__scanline {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .bg__rain {
    display: none;
  }
}
</style>
