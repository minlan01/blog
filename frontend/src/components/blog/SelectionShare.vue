<template>
  <Teleport to="body">
    <Transition name="share-popup">
      <div
        v-if="visible"
        class="share-select"
        :style="{ left: `${position.x}px`, top: `${position.y}px` }"
      >
        <button class="share-select__btn" @click="copyText" title="复制选中文本">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          <span>复制</span>
        </button>
        <button class="share-select__btn share-select__btn--accent" @click="shareToTwitter" title="分享到 Twitter">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"/></svg>
          <span>Twitter</span>
        </button>
        <button class="share-select__btn" @click="shareToWeibo" title="分享到微博">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M10.098 20.323c-3.977.391-7.414-1.406-7.672-4.02-.259-2.609 2.759-5.047 6.74-5.441 3.979-.394 7.413 1.404 7.671 4.018.259 2.6-2.759 5.049-6.739 5.443z"/></svg>
          <span>微博</span>
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const visible = ref(false)
const position = ref({ x: 0, y: 0 })
const selectedText = ref('')
const pageUrl = ref('')
const pageTitle = ref('')

function getSelectionInfo() {
  const sel = window.getSelection()
  if (!sel || sel.isCollapsed || sel.rangeCount === 0) {
    visible.value = false
    return
  }

  const text = sel.toString().trim()
  if (text.length < 2 || text.length > 280) {
    visible.value = false
    return
  }

  selectedText.value = text
  pageUrl.value = window.location.href
  pageTitle.value = document.title

  // Position the popup near the selection
  const range = sel.getRangeAt(0)
  const rect = range.getBoundingClientRect()
  position.value = {
    x: rect.left + rect.width / 2,
    y: rect.top - 10,
  }

  // Adjust if popup would go off-screen
  const popupWidth = 200
  if (position.value.x + popupWidth / 2 > window.innerWidth) {
    position.value.x = window.innerWidth - popupWidth / 2 - 10
  }
  if (position.value.x - popupWidth / 2 < 10) {
    position.value.x = popupWidth / 2 + 10
  }

  visible.value = true
}

function hide() {
  visible.value = false
}

async function copyText() {
  try {
    await navigator.clipboard.writeText(selectedText.value)
    hide()
  } catch {
    // Fallback
    const ta = document.createElement('textarea')
    ta.value = selectedText.value
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    hide()
  }
}

function shareToTwitter() {
  const quote = `"${selectedText.value}"`
  const text = encodeURIComponent(`${quote}\n\n${pageTitle.value}\n${pageUrl.value}`)
  window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank', 'noopener')
  hide()
}

function shareToWeibo() {
  const text = encodeURIComponent(`${selectedText.value}\n\n${pageUrl.value}`)
  window.open(`https://service.weibo.com/share/share.php?url=${encodeURIComponent(pageUrl.value)}&title=${text}`, '_blank', 'noopener')
  hide()
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null

function onMouseUp() {
  // Debounce to allow selection to finalize
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(getSelectionInfo, 10)
}

function onScroll() {
  if (visible.value) hide()
}

onMounted(() => {
  document.addEventListener('mouseup', onMouseUp)
  document.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  document.removeEventListener('mouseup', onMouseUp)
  document.removeEventListener('scroll', onScroll)
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<style scoped>
.share-select {
  position: fixed;
  transform: translate(-50%, -100%);
  display: flex;
  gap: 2px;
  padding: 6px;
  background: var(--glass-panel-bg, rgba(15, 15, 30, 0.95));
  backdrop-filter: blur(16px) saturate(1.5);
  -webkit-backdrop-filter: blur(16px) saturate(1.5);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  z-index: 1000;
}

.share-select__btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border: none;
  background: none;
  color: var(--color-text-soft, #ccc);
  font-size: 0.8rem;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast) ease;
}

.share-select__btn:hover {
  background: var(--color-surface-hover, rgba(255, 255, 255, 0.08));
  color: var(--color-text);
}

.share-select__btn--accent:hover {
  color: var(--color-accent, #818cf8);
}

.share-select__btn svg {
  flex-shrink: 0;
}

.share-select__btn span {
  font-weight: 500;
}

.share-popup-enter-active,
.share-popup-leave-active {
  transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
}

.share-popup-enter-from,
.share-popup-leave-to {
  opacity: 0;
  transform: translate(-50%, calc(-100% + 8px));
}
</style>
