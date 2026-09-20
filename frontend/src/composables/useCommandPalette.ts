import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

interface CommandItem {
  id: string
  label: string
  hint?: string
  action: () => void
}

interface FuseResult {
  item: CommandItem
  score: number
}

/**
 * Command palette (Ctrl+K) - quick navigation.
 * Lightweight fuzzy match without external dependency.
 */
export function useCommandPalette() {
  const router = useRouter()
  const open = ref(false)
  const query = ref('')
  const items = ref<CommandItem[]>([])
  const selectedIndex = ref(0)
  const filtered = ref<CommandItem[]>([])

  function fuzzyMatch(text: string, q: string): boolean {
    const textLower = text.toLowerCase()
    const qLower = q.toLowerCase()
    if (textLower.includes(qLower)) return true
    // Simple subsequence match
    let qi = 0
    for (let ti = 0; ti < textLower.length && qi < qLower.length; ti++) {
      if (textLower[ti] === qLower[qi]) qi++
    }
    return qi === qLower.length
  }

  function filter() {
    if (!query.value.trim()) {
      filtered.value = items.value
    } else {
      filtered.value = items.value.filter((item) =>
        fuzzyMatch(item.label, query.value) ||
        (item.hint && fuzzyMatch(item.hint, query.value))
      )
    }
    selectedIndex.value = 0
  }

  function addCommands(commands: CommandItem[]) {
    items.value.push(...commands)
    filter()
  }

  function execute(item: CommandItem) {
    open.value = false
    query.value = ''
    item.action()
  }

  function onKeydown(e: KeyboardEvent) {
    // Ctrl+K / Cmd+K toggles
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault()
      open.value = !open.value
      if (!open.value) {
        query.value = ''
      }
      filter()
      return
    }

    if (!open.value) return

    // Escape closes
    if (e.key === 'Escape') {
      open.value = false
      query.value = ''
      return
    }

    // Arrow navigation
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      selectedIndex.value = (selectedIndex.value + 1) % filtered.value.length
      return
    }

    if (e.key === 'ArrowUp') {
      e.preventDefault()
      selectedIndex.value = (selectedIndex.value - 1 + filtered.value.length) % filtered.value.length
      return
    }

    // Enter executes
    if (e.key === 'Enter' && filtered.value.length > 0) {
      e.preventDefault()
      execute(filtered.value[selectedIndex.value])
      return
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', onKeydown)
    // Default commands
    addCommands([
      { id: 'home', label: '首页', hint: 'Go to homepage', action: () => router.push('/') },
      { id: 'posts', label: '文章列表', hint: 'Browse all posts', action: () => router.push('/posts') },
      { id: 'archive', label: '归档', hint: 'View archive', action: () => router.push('/archive') },
      { id: 'about', label: '关于', hint: 'About page', action: () => router.push('/about') },
      { id: 'links', label: '友链', hint: 'Friend links', action: () => router.push('/link') },
      { id: 'message', label: '留言板', hint: 'Leave a message', action: () => router.push('/message-board') },
      { id: 'admin', label: '管理后台', hint: 'Admin panel', action: () => router.push('/admin') },
      { id: 'create', label: '写文章', hint: 'Create new post', action: () => router.push('/create-post') },
    ])
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', onKeydown)
  })

  return {
    open,
    query,
    filtered,
    selectedIndex,
    filter,
    execute,
    addCommands,
  }
}
