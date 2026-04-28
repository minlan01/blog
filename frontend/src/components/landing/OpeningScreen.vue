<template>
  <Transition name="opening-exit">
    <div v-if="visible" class="opening" @wheel.prevent="handleScroll">
      <!-- Matrix rain canvas -->
      <canvas ref="matrixCanvas" class="opening__matrix"></canvas>

      <div class="opening__content">
        <div class="opening__terminal">
          <div class="opening__terminal-bar">
            <span class="opening__dot opening__dot--red"></span>
            <span class="opening__dot opening__dot--yellow"></span>
            <span class="opening__dot opening__dot--green"></span>
            <span class="opening__terminal-title">terminal</span>
          </div>
          <div class="opening__terminal-body">
            <p class="opening__prompt">
              <span class="opening__user">minlan01</span><span class="opening__at">@</span><span class="opening__host">blog</span><span class="opening__colon">:</span><span class="opening__path">~</span><span class="opening__dollar">$</span>
              <span class="opening__cmd">{{ displayedCmd }}<span class="opening__cursor">_</span></span>
            </p>
            <div class="opening__output" v-if="showOutput">
              <p v-for="(line, i) in titleLines" :key="i" class="opening__output-line" :style="{ animationDelay: `${i * 0.3}s` }">{{ line }}</p>
              <p class="opening__output-sub" style="animation-delay: 0.6s">{{ subtitle }}</p>
            </div>
          </div>
        </div>

        <div class="opening__actions">
          <button class="opening__enter-btn" @click="handleEnter">
            <span class="opening__btn-bracket">[</span>
            <span>ENTER</span>
            <span class="opening__btn-bracket">]</span>
          </button>
          <RouterLink class="opening__secondary-link" to="/posts">> cat posts.log</RouterLink>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = withDefaults(defineProps<{
  title?: string
  subtitle?: string
  kicker?: string
}>(), {
  title: 'SYSTEM ONLINE\nACCESS GRANTED',
  subtitle: '// Terminal blog system ready.',
  kicker: 'TERMINAL'
})

const emit = defineEmits<{
  (e: 'enter'): void
}>()

const visible = ref(true)
const showOutput = ref(false)
const displayedCmd = ref('')
const matrixCanvas = ref<HTMLCanvasElement | null>(null)
let scrollAccum = 0
let animFrame = 0
let cmdTimer: ReturnType<typeof setTimeout> | null = null

const titleLines = computed(() => props.title.split('\n'))
const fullCmd = './blog --init --mode=hacker'

// Typing effect
function typeCmd() {
  let i = 0
  const interval = setInterval(() => {
    if (i < fullCmd.length) {
      displayedCmd.value = fullCmd.slice(0, i + 1)
      i++
    } else {
      clearInterval(interval)
      showOutput.value = true
    }
  }, 60)
}

// Matrix rain
function initMatrix() {
  if (!matrixCanvas.value) return
  const canvas: HTMLCanvasElement = matrixCanvas.value
  const ctx: CanvasRenderingContext2D = canvas.getContext('2d')!

  canvas.width = window.innerWidth
  canvas.height = window.innerHeight

  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*(){}[]|;:<>?/~`'
  const fontSize = 14
  const columns = Math.floor(canvas.width / fontSize)
  const drops: number[] = Array(columns).fill(1)

  function draw() {
    ctx.fillStyle = 'rgba(10, 10, 10, 0.05)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = 'rgba(0, 255, 65, 0.15)'
    ctx.font = `${fontSize}px "JetBrains Mono", monospace`

    for (let i = 0; i < drops.length; i++) {
      const char = chars[Math.floor(Math.random() * chars.length)]
      ctx.fillText(char, i * fontSize, drops[i] * fontSize)
      if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
        drops[i] = 0
      }
      drops[i]++
    }
    animFrame = requestAnimationFrame(draw)
  }
  draw()
}

function handleEnter() {
  visible.value = false
  setTimeout(() => emit('enter'), 500)
}

function handleScroll(e: WheelEvent) {
  scrollAccum += Math.abs(e.deltaY)
  if (scrollAccum > 200) {
    handleEnter()
  }
}

function handleResize() {
  if (matrixCanvas.value) {
    matrixCanvas.value.width = window.innerWidth
    matrixCanvas.value.height = window.innerHeight
  }
}

onMounted(() => {
  initMatrix()
  setTimeout(typeCmd, 400)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  cancelAnimationFrame(animFrame)
  if (cmdTimer) clearTimeout(cmdTimer)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.opening-exit-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.opening-exit-leave-to {
  opacity: 0;
  transform: scale(0.98);
}

.opening {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #0a0a0a;
  overflow: hidden;
}

.opening__matrix {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.opening__content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: left;
  padding: var(--space-lg);
  max-width: 700px;
  width: 100%;
  margin: auto 0;
}

/* Terminal Window */
.opening__terminal {
  width: 100%;
  background: rgba(13, 13, 13, 0.75);
  backdrop-filter: blur(100px);
  -webkit-backdrop-filter: blur(100px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow:
    0 0 40px rgba(0, 255, 65, 0.12),
    0 0 80px rgba(0, 255, 65, 0.06),
    inset 0 0 30px rgba(0, 255, 65, 0.04);
}

.opening__terminal-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: #111;
  border-bottom: 1px solid var(--color-border);
}

.opening__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.opening__dot--red { background: #ff5f57; }
.opening__dot--yellow { background: #febc2e; }
.opening__dot--green { background: #28c840; }

.opening__terminal-title {
  margin-left: auto;
  font-size: 0.72rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  letter-spacing: 0.05em;
}

.opening__terminal-body {
  padding: var(--space-lg);
  font-family: var(--font-mono);
  font-size: 0.85rem;
  line-height: 1.8;
}

.opening__prompt {
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
}

.opening__user { color: #39ff14; font-weight: 600; }
.opening__at { color: var(--color-text-muted); }
.opening__host { color: #00cc00; }
.opening__colon { color: var(--color-text-muted); }
.opening__path { color: #ffb000; }
.opening__dollar { color: var(--color-text); margin-right: 8px; }

.opening__cmd {
  color: var(--color-text);
}

.opening__cursor {
  animation: blink 1s step-end infinite;
  color: var(--color-accent);
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.opening__output {
  margin-top: var(--space-sm);
}

.opening__output-line {
  color: var(--color-text-heading);
  font-size: 1.1rem;
  font-weight: 600;
  text-shadow: 0 0 8px rgba(0, 255, 65, 0.3);
  animation: fadeIn 0.5s ease forwards;
  opacity: 0;
}

.opening__output-sub {
  color: var(--color-text-muted);
  font-size: 0.8rem;
  margin-top: var(--space-sm);
  animation: fadeIn 0.5s ease forwards;
  opacity: 0;
}

@keyframes fadeIn {
  to { opacity: 1; }
}

/* Actions */
.opening__actions {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  margin-top: var(--space-2xl);
}

.opening__enter-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 12px 28px;
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm);
  color: var(--color-accent);
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 0.9rem;
  background: transparent;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  transition: all var(--duration-fast) ease;
}

.opening__enter-btn:hover {
  background: rgba(0, 255, 65, 0.1);
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
  text-shadow: 0 0 6px rgba(0, 255, 65, 0.4);
}

.opening__btn-bracket {
  color: var(--color-text-muted);
  transition: color var(--duration-fast) ease;
}

.opening__enter-btn:hover .opening__btn-bracket {
  color: var(--color-accent);
}

.opening__secondary-link {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--color-text-muted);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 2px;
  transition: all var(--duration-fast) ease;
}

.opening__secondary-link:hover {
  color: var(--color-accent);
  border-color: var(--color-accent);
  text-shadow: 0 0 6px rgba(0, 255, 65, 0.4);
}

@media (max-width: 640px) {
  .opening__actions {
    flex-direction: column;
    gap: var(--space-md);
  }
  .opening__enter-btn {
    width: 100%;
    justify-content: center;
  }
  .opening__terminal-body {
    font-size: 0.75rem;
  }
  .opening__output-line {
    font-size: 0.9rem;
  }
}
</style>
