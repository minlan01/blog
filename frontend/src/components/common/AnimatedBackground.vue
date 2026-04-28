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

const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%&*{}[];:<>?/~'
const FONT_SIZE = 15

function init() {
  if (!canvas.value) return
  const el: HTMLCanvasElement = canvas.value
  const ctx: CanvasRenderingContext2D = el.getContext('2d')!

  function resize() {
    el.width = window.innerWidth
    el.height = window.innerHeight
  }
  resize()
  window.addEventListener('resize', resize)
  resizeHandler = resize

  const columns = Math.floor(el.width / FONT_SIZE)
  const drops: number[] = Array(columns).fill(0).map(() => Math.random() * -100)

  function draw() {
    const isLight = theme.value === 'light'

    // Fadeout overlay — matches the background color for natural trail decay
    ctx.fillStyle = isLight ? 'rgba(250, 247, 242, 0.05)' : 'rgba(10, 10, 10, 0.05)'
    ctx.fillRect(0, 0, el.width, el.height)

    ctx.font = `${FONT_SIZE}px "JetBrains Mono", monospace`

    for (let i = 0; i < drops.length; i++) {
      const char = CHARS[Math.floor(Math.random() * CHARS.length)]
      const y = drops[i] * FONT_SIZE

      // Head color
      if (isLight) {
        ctx.fillStyle = 'rgba(217, 119, 6, 0.40)'
      } else {
        ctx.fillStyle = 'rgba(0, 255, 65, 0.5)'
      }
      ctx.fillText(char, i * FONT_SIZE, y)

      // Trail
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

  draw()
}

onMounted(init)

onUnmounted(() => {
  cancelAnimationFrame(animFrame)
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
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

/* Ambient glow — adds depth behind the rain */
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

/* Scanlines */
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

@media (prefers-reduced-motion: reduce) {
  .bg__rain {
    display: none;
  }
}
</style>
