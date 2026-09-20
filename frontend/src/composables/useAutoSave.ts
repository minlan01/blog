import { watch, onMounted, onUnmounted, type Ref } from 'vue'

interface AutoSaveData {
  title?: string
  content_markdown?: string
  summary?: string
  [key: string]: any
}

/**
 * 编辑器自动保存 composable
 * 每 30 秒或内容变化后 5 秒（防抖）将草稿保存到 localStorage
 * 页面加载时如检测到草稿，提示用户恢复
 */
const SAVE_INTERVAL = 30 * 1000       // 定时保存间隔
const DEBOUNCE_DELAY = 5 * 1000       // 内容变化后防抖延迟
const MAX_DRAFT_AGE = 24 * 3600 * 1000 // 草稿最大保留时长（24 小时）

export function useAutoSave(key: string, form: Ref<AutoSaveData>) {
  const storageKey = `draft:${key}`

  function loadDraft(): AutoSaveData | null {
    try {
      const raw = localStorage.getItem(storageKey)
      if (!raw) return null
      const data = JSON.parse(raw)
      // 过期草稿不恢复
      if (Date.now() - (data.__savedAt || 0) > MAX_DRAFT_AGE) {
        localStorage.removeItem(storageKey)
        return null
      }
      return data
    } catch {
      return null
    }
  }

  function saveDraft() {
    try {
      const payload = { ...form.value, __savedAt: Date.now() }
      localStorage.setItem(storageKey, JSON.stringify(payload))
    } catch {
      // localStorage 满或被禁用，静默失败
    }
  }

  function clearDraft() {
    localStorage.removeItem(storageKey)
  }

  // 防抖保存
  let debounceTimer: ReturnType<typeof setTimeout> | null = null
  function debouncedSave() {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(saveDraft, DEBOUNCE_DELAY)
  }

  // 监听内容变化
  let stopWatch: (() => void) | null = null

  onMounted(() => {
    stopWatch = watch(
      () => form.value,
      () => debouncedSave(),
      { deep: true }
    )
    // 定时保存
    const intervalId = setInterval(saveDraft, SAVE_INTERVAL)
    // 页面隐藏时保存
    const onVisibilityChange = () => {
      if (document.visibilityState === 'hidden') saveDraft()
    }
    document.addEventListener('visibilitychange', onVisibilityChange)

    onUnmounted(() => {
      if (stopWatch) stopWatch()
      clearInterval(intervalId)
      document.removeEventListener('visibilitychange', onVisibilityChange)
      if (debounceTimer) clearTimeout(debounceTimer)
      // 卸载时最后保存一次
      saveDraft()
    })
  })

  return { loadDraft, saveDraft, clearDraft }
}
