<template>
  <RouterView v-slot="{ Component }">
    <component :is="Component" />
  </RouterView>
  <MusicWidget v-if="showMusicWidget" />
  <ToastContainer />
  <CommandPalette />
  <SelectionShare />
</template>

<script setup lang="ts">
import { computed, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import ToastContainer from '@/components/common/ToastContainer.vue'
import CommandPalette from '@/components/common/CommandPalette.vue'
import SelectionShare from '@/components/blog/SelectionShare.vue'
import MusicWidget from '@/components/sidebar/MusicWidget.vue'

const route = useRoute()

// 音乐播放器全局显示，但后台管理和编辑页面不显示
const showMusicWidget = computed(() => {
  const path = route.path
  return !path.startsWith('/admin') &&
         !path.startsWith('/create-post') &&
         !path.startsWith('/edit-post') &&
         !path.startsWith('/login')
})

// Trigger View Transitions for SPA navigation (same-document)
// Only applies when the browser supports startViewTransition.
// The shared-element effect (post-card → post-title etc.) relies on
// matching view-transition-name on both pages.
watch(
  () => route.fullPath,
  (_newPath, oldPath) => {
    if (oldPath === undefined) return // skip initial load
    if (typeof document === 'undefined' || !document.startViewTransition) return

    // The DOM swap is handled by Vue Router automatically.
    // We just need to wrap the tick in a view transition.
    document.startViewTransition(async () => {
      await nextTick()
    })
  }
)
</script>
