import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useToastStore } from '@/stores/toast'

describe('Toast Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  it('shows a toast message', () => {
    const store = useToastStore()
    store.show('Hello', 'info')
    expect(store.items).toHaveLength(1)
    expect(store.items[0].message).toBe('Hello')
    expect(store.items[0].type).toBe('info')
  })

  it('removes toast after duration', () => {
    const store = useToastStore()
    store.show('Test', 'success', 1000)
    expect(store.items).toHaveLength(1)

    vi.advanceTimersByTime(1000)
    expect(store.items).toHaveLength(0)
  })

  it('success helper creates success toast', () => {
    const store = useToastStore()
    store.success('Done!')
    expect(store.items[0].type).toBe('success')
    expect(store.items[0].message).toBe('Done!')
  })

  it('error helper creates error toast with longer duration', () => {
    const store = useToastStore()
    store.error('Oops')
    expect(store.items[0].type).toBe('error')
    expect(store.items[0].duration).toBe(5000)
  })

  it('manually removes a toast', () => {
    const store = useToastStore()
    store.show('A')
    store.show('B')
    store.remove(store.items[0].id)
    expect(store.items).toHaveLength(1)
    expect(store.items[0].message).toBe('B')
  })
})
