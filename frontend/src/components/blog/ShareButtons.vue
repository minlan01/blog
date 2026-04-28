<template>
  <div class="share-buttons">
    <span class="share-buttons__label">分享：</span>
    <button class="share-btn share-btn--weibo" @click="shareToWeibo" title="分享到微博">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M10.098 20.323c-3.977.391-7.414-1.406-7.672-4.02-.259-2.609 2.759-5.047 6.74-5.441 3.979-.394 7.413 1.404 7.671 4.018.259 2.6-2.759 5.049-6.739 5.443zM9.05 17.219c-.384.616-1.208.884-1.829.602-.612-.279-.793-.991-.406-1.593.379-.595 1.176-.861 1.793-.583.631.283.822.985.442 1.574zm1.27-1.627c-.141.237-.449.353-.689.253-.236-.09-.307-.361-.164-.586.141-.226.433-.34.672-.246.24.09.315.36.181.579zm.176-2.719c-1.893-.494-4.033.45-4.857 2.118-.836 1.704-.026 3.591 1.886 4.21 1.983.642 4.318-.341 5.132-2.145.8-1.74-.139-3.656-2.161-4.183zM17.616 4.512c-.389-.115-.645-.187-.445-.694.435-1.078.48-2.007.009-2.672-.885-1.254-3.311-1.188-6.082-.034 0 0-.871.384-.649-.313.428-1.394.364-2.564-.304-3.233C8.797-3.514 5.561-2.1 2.814.826.737 3.043-.319 5.454-.319 7.589c0 4.079 5.226 6.566 10.338 6.566 6.718 0 11.185-3.927 11.185-7.058 0-1.886-1.582-2.953-3.588-3.585z"/></svg>
    </button>
    <button class="share-btn share-btn--twitter" @click="shareToTwitter" title="分享到 Twitter">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
    </button>
    <button class="share-btn share-btn--copy" @click="copyLink" title="复制链接">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
      <span v-if="copied" class="share-btn__tip">已复制</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  title: string
  url?: string
}>()

const copied = ref(false)

function getShareUrl() {
  return props.url || window.location.href
}

function shareToWeibo() {
  const url = `https://service.weibo.com/share/share.php?url=${encodeURIComponent(getShareUrl())}&title=${encodeURIComponent(props.title)}`
  window.open(url, '_blank', 'width=600,height=400')
}

function shareToTwitter() {
  const url = `https://twitter.com/intent/tweet?url=${encodeURIComponent(getShareUrl())}&text=${encodeURIComponent(props.title)}`
  window.open(url, '_blank', 'width=600,height=400')
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(getShareUrl())
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // fallback
  }
}
</script>

<style scoped>
.share-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}
.share-buttons__label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
.share-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--glass-card-bg);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}
.share-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  transform: translateY(-1px);
}
.share-btn--weibo:hover { color: #e6162d; border-color: #e6162d; }
.share-btn--twitter:hover { color: #1da1f2; border-color: #1da1f2; }
.share-btn__tip {
  position: absolute;
  bottom: -24px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.7rem;
  color: #4ade80;
  white-space: nowrap;
}
</style>
