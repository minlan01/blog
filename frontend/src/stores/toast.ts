import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ToastItem {
  id: number
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration: number
}

let nextId = 0

export const useToastStore = defineStore('toast', () => {
  const items = ref<ToastItem[]>([])

  function show(message: string, type: ToastItem['type'] = 'info', duration = 3000) {
    const id = nextId++
    items.value.push({ id, message, type, duration })
    if (duration > 0) {
      setTimeout(() => remove(id), duration)
    }
  }

  function remove(id: number) {
    items.value = items.value.filter(t => t.id !== id)
  }

  function success(message: string) { show(message, 'success') }
  function error(message: string) { show(message, 'error', 5000) }
  function warning(message: string) { show(message, 'warning', 4000) }
  function info(message: string) { show(message, 'info') }

  return { items, show, remove, success, error, warning, info }
})
