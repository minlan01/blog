<template>
  <div class="music-widget" :class="{ 'music-widget--collapsed': !expanded }">
    <!-- audio 永远存在于 DOM 中，不受面板展开/收起影响 -->
    <audio
      ref="audioEl"
      preload="metadata"
      :src="currentTrack?.url"
      @ended="playNext"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMeta"
      @canplay="onCanPlay"
      @waiting="switching = true"
      @playing="onAudioPlaying"
      @pause="playing = false"
    ></audio>

    <!-- 折叠态：上一首 / 播放暂停 / 下一首 / 展开 -->
    <div v-if="!expanded" class="music-widget__fab-group">
      <button class="music-widget__fab-sm" @click="playPrev" title="上一首" :disabled="tracks.length <= 1">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
      </button>
      <button class="music-widget__fab" @click="togglePlay" :title="playing ? '暂停' : '播放'">
        <svg v-if="!playing" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M6 4h4v16H6zm8 0h4v16h-4z"/></svg>
        <span v-if="playing" class="music-widget__fab-pulse"></span>
      </button>
      <button class="music-widget__fab-sm" @click="playNext" title="下一首" :disabled="tracks.length <= 1">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
      </button>
      <div class="music-widget__fab-divider"></div>
      <button class="music-widget__fab-expand" @click="expand" title="展开播放列表">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
      </button>
    </div>

    <!-- 展开态：遮罩 + 面板（v-show 保持 DOM 存在） -->
    <div v-show="expanded" class="music-widget__backdrop" @click="collapse"></div>
    <div v-show="expanded" class="music-widget__panel">
      <div class="music-widget__header">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
        <span>音乐</span>
        <button class="music-widget__close" @click="collapse" title="收起">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>

      <div v-if="loading" class="music-widget__loading">加载中...</div>
      <div v-else-if="tracks.length === 0" class="music-widget__empty">暂无音乐</div>

      <div v-else class="music-widget__body">
        <div class="music-widget__now-playing">
          <div class="music-widget__track-name" :title="currentTrack?.filename">
            {{ currentTrack?.filename || '未选择' }}
          </div>
        </div>

        <div class="music-widget__progress" @click="seek">
          <div class="music-widget__progress-bar" :style="{ width: progressPercent + '%' }"></div>
        </div>

        <div class="music-widget__time">
          <span>{{ formatTime(currentTime) }}</span>
          <span>{{ formatTime(duration) }}</span>
        </div>

        <div class="music-widget__controls">
        <button class="music-widget__btn" @click="playPrev" title="上一首" :disabled="tracks.length <= 1 || switching">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
              </button>
              <button class="music-widget__btn music-widget__btn--play" @click="togglePlay" :title="playing ? '暂停' : '播放'" :disabled="switching">
                <svg v-if="switching" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin-icon"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                <svg v-else-if="!playing" width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M6 4h4v16H6zm8 0h4v16h-4z"/></svg>
              </button>
              <button class="music-widget__btn" @click="playNext" title="下一首" :disabled="tracks.length <= 1 || switching">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
              </button>
        </div>

        <div v-if="tracks.length > 1" class="music-widget__playlist">
          <div
            v-for="(track, i) in tracks"
            :key="track.id"
            class="music-widget__track"
            :class="{ active: i === currentIndex }"
            @click="selectTrack(i)"
          >
            <span class="music-widget__track-num">{{ i + 1 }}</span>
            <span class="music-widget__track-title" :title="track.filename">{{ track.filename }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { getMusicTracks, type MusicTrack } from '@/api/admin'

const tracks = ref<MusicTrack[]>([])
const loading = ref(true)
const expanded = ref(false)
const currentIndex = ref(0)
const playing = ref(false)
const switching = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const wantPlay = ref(false) // 标记是否应该自动播放
const audioEl = ref<HTMLAudioElement | null>(null)

const currentTrack = computed(() => tracks.value[currentIndex.value] || null)
const progressPercent = computed(() => duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0)

async function loadTracks() {
  loading.value = true
  try {
    tracks.value = await getMusicTracks()
  } catch {
    tracks.value = []
  }
  loading.value = false
}

function expand() {
  expanded.value = true
}

function collapse() {
  expanded.value = false
  // 收起时不停音乐
}

function togglePlay() {
  if (!audioEl.value) return
  if (playing.value) {
    audioEl.value.pause()
    playing.value = false
  } else {
    wantPlay.value = true
    audioEl.value.play().catch(() => {})
  }
}

function selectTrack(i: number) {
  if (i === currentIndex.value) return
  // 切歌前先暂停当前播放，避免并发加载
  if (audioEl.value) {
    audioEl.value.pause()
  }
  switching.value = true
  playing.value = false
  wantPlay.value = true // 用户点了歌就自动播
  currentIndex.value = i
}

function playNext() {
  if (tracks.value.length <= 1) return
  if (audioEl.value) audioEl.value.pause()
  switching.value = true
  playing.value = false
  wantPlay.value = true
  currentIndex.value = (currentIndex.value + 1) % tracks.value.length
}

function playPrev() {
  if (tracks.value.length <= 1) return
  if (audioEl.value) audioEl.value.pause()
  switching.value = true
  playing.value = false
  wantPlay.value = true
  currentIndex.value = (currentIndex.value - 1 + tracks.value.length) % tracks.value.length
}

// audio src 变化后，canplay 事件触发时自动播放
function onAudioPlaying() {
  switching.value = false
  playing.value = true
}

function onCanPlay() {
  switching.value = false
  if (wantPlay.value && audioEl.value) {
    audioEl.value.play().then(() => {
      playing.value = true
    }).catch(() => {
      playing.value = false
    })
    wantPlay.value = false
  }
}

function onTimeUpdate() {
  if (audioEl.value) currentTime.value = audioEl.value.currentTime
}

function onLoadedMeta() {
  if (audioEl.value) duration.value = audioEl.value.duration
}

function seek(e: MouseEvent) {
  if (!audioEl.value || duration.value === 0) return
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  const percent = (e.clientX - rect.left) / rect.width
  audioEl.value.currentTime = percent * duration.value
}

function formatTime(s: number): string {
  if (!s || isNaN(s)) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${String(sec).padStart(2, '0')}`
}

// 监听 expanded 变化，收起时不停音乐
watch(expanded, (val) => {
  // 音乐继续播放，只是面板隐藏
})

onMounted(() => {
  loadTracks()
})
</script>

<style scoped>
/* 全局固定定位（左下角），不拦截点击 */
.music-widget {
  position: fixed;
  left: 16px;
  bottom: 16px;
  z-index: 50;
  pointer-events: none;
}

@media (max-width: 768px) {
  .music-widget {
    left: 12px;
    bottom: 12px;
  }
}

.music-widget__fab-group,
.music-widget__fab,
.music-widget__fab-sm,
.music-widget__fab-expand {
  pointer-events: auto;
}

/* audio 元素完全隐藏，不占空间不拦截事件 */
.music-widget audio {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}

.music-widget__fab-group {
  display: flex;
  align-items: center;
  gap: 2px;
  border-radius: 28px;
  padding: 2px;
  background: var(--glass-card-bg);
  border: 1px solid var(--glass-border);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  box-shadow: var(--glass-card-shadow);
}

.music-widget__fab {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--color-text-soft);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  position: relative;
}

.music-widget__fab:hover {
  color: var(--color-accent);
}

.music-widget__fab-pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid var(--color-accent);
  animation: music-pulse 1.5s ease-out infinite;
}

.music-widget__fab-sm {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.music-widget__fab-sm:hover:not(:disabled) {
  color: var(--color-accent);
  background: var(--accent-tint-06);
}

.music-widget__fab-sm:disabled {
  opacity: 0.25;
  cursor: not-allowed;
}

.music-widget__fab-divider {
  width: 1px;
  height: 20px;
  background: var(--glass-border);
  margin: 0 2px;
}

.music-widget__fab-expand {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.music-widget__fab-expand:hover {
  color: var(--color-accent);
  background: var(--accent-tint-06);
}

@keyframes music-pulse {
  0% { opacity: 0.8; transform: scale(1); }
  100% { opacity: 0; transform: scale(1.4); }
}

/* 遮罩：点击空白关闭面板 */
.music-widget__backdrop {
  position: fixed;
  inset: 0;
  z-index: 998;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(2px);
}

.music-widget__panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 480px;
  max-width: calc(100vw - 32px);
  max-height: 85vh;
  overflow-y: auto;
  z-index: 999;
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.25);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.music-widget__header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: var(--space-md);
}

.music-widget__close {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 2px;
  display: flex;
  transition: color 0.15s ease;
}

.music-widget__close:hover {
  color: var(--error-main);
}

.music-widget__loading,
.music-widget__empty {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  text-align: center;
  padding: var(--space-md) 0;
}

.music-widget__now-playing {
  margin-bottom: 12px;
}

.music-widget__track-name {
  font-size: 1rem;
  color: var(--color-text);
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.music-widget__progress {
  width: 100%;
  height: 6px;
  background: var(--glass-bg-08);
  border-radius: 3px;
  cursor: pointer;
  margin-bottom: 6px;
}

.music-widget__progress-bar {
  height: 100%;
  background: var(--color-accent);
  border-radius: 3px;
  transition: width 0.15s linear;
}

.music-widget__time {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  margin-bottom: 14px;
}

.music-widget__controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  margin-bottom: 14px;
}

.music-widget__btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: var(--glass-bg-08);
  color: var(--color-text-soft);
  cursor: pointer;
  transition: all 0.15s ease;
}

.music-widget__btn:hover:not(:disabled) {
  background: var(--accent-tint-15);
  color: var(--color-accent);
}

.music-widget__btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.music-widget__btn--play {
  width: 48px;
  height: 48px;
  background: var(--color-accent);
  color: #fff;
}

.music-widget__btn--play:hover {
  opacity: 0.9;
  background: var(--color-accent);
}

.spin-icon {
  animation: spin 1s linear infinite;
}

.music-widget__playlist {
  max-height: 200px;
  overflow-y: auto;
  border-top: 1px solid var(--glass-border);
  padding-top: 12px;
  margin-top: 8px;
}

.music-widget__track {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.15s ease;
}

.music-widget__track:hover {
  background: var(--glass-bg-06);
}

.music-widget__track.active {
  background: var(--accent-tint-12);
}

.music-widget__track-num {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  flex-shrink: 0;
  width: 20px;
  text-align: right;
}

.music-widget__track.active .music-widget__track-num {
  color: var(--color-accent);
}

.music-widget__track-title {
  font-size: 0.85rem;
  color: var(--color-text-soft);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.music-widget__track.active .music-widget__track-title {
  color: var(--color-accent);
  font-weight: 500;
}

/* 遮罩和面板只在展开时接收点击 */
.music-widget__backdrop,
.music-widget__panel {
  pointer-events: none;
}

.music-widget:not(.music-widget--collapsed) .music-widget__backdrop,
.music-widget:not(.music-widget--collapsed) .music-widget__panel {
  pointer-events: auto;
}

/* 面板显隐过渡 */
.music-widget__backdrop {
  opacity: 1;
  transition: opacity 0.2s ease;
}

.music-widget__panel {
  opacity: 1;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

/* v-show hidden 时通过 CSS 控制 */
.music-widget__panel[style*="display: none"] {
  /* nothing needed, v-show handles display */
}

@media (max-width: 768px) {
  .music-widget__panel {
    width: calc(100vw - 32px);
    max-height: 70vh;
  }
}
</style>
