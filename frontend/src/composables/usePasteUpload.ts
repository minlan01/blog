import { onMounted, onUnmounted, type Ref } from 'vue'
import { useImageUpload } from '@/composables/useImageUpload'
import { useToastStore } from '@/stores/toast'

/**
 * Composable: paste image into editor auto-uploads.
 * Listens for paste events on the editor element and uploads image files.
 */
export function usePasteUpload(contentRef: Ref<string>, editorSelector = '.md-editor') {
  const { uploading, uploadImage } = useImageUpload()
  const toast = useToastStore()

  async function handlePaste(e: ClipboardEvent) {
    if (!e.clipboardData?.items) return

    const items = Array.from(e.clipboardData.items)
    const imageItems = items.filter((item) => item.type.startsWith('image/'))

    if (imageItems.length === 0) return

    e.preventDefault()

    for (const item of imageItems) {
      const file = item.getAsFile()
      if (!file) continue

      // Generate placeholder markdown
      const placeholder = `![上传中...](uploading-${Date.now()})`
      contentRef.value += `\n${placeholder}\n`

      const url = await uploadImage(file)
      if (url) {
        contentRef.value = contentRef.value.replace(placeholder, `![${file.name || 'image'}](${url})`)
      } else {
        // Remove placeholder on failure
        contentRef.value = contentRef.value.replace(`\n${placeholder}\n`, '')
        toast.error('图片上传失败')
      }
    }
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault()
    const editor = e.currentTarget as HTMLElement
    editor.classList.add('editor__md-editor--drag-over')
  }

  function handleDragLeave(e: DragEvent) {
    const editor = e.currentTarget as HTMLElement
    editor.classList.remove('editor__md-editor--drag-over')
  }

  async function handleDrop(e: DragEvent) {
    if (!e.dataTransfer?.files) return
    const files = Array.from(e.dataTransfer.files).filter((f) => f.type.startsWith('image/'))
    if (files.length === 0) return

    e.preventDefault()
    const editor = e.currentTarget as HTMLElement
    editor.classList.remove('editor__md-editor--drag-over')

    for (const file of files) {
      const placeholder = `![上传中...](uploading-${Date.now()})`
      contentRef.value += `\n${placeholder}\n`

      const url = await uploadImage(file)
      if (url) {
        contentRef.value = contentRef.value.replace(placeholder, `![${file.name || 'image'}](${url})`)
      } else {
        contentRef.value = contentRef.value.replace(`\n${placeholder}\n`, '')
        toast.error('图片上传失败')
      }
    }
  }

  function setup() {
    const editor = document.querySelector(editorSelector)
    if (editor) {
      editor.addEventListener('paste', handlePaste as unknown as EventListener)
      editor.addEventListener('dragover', handleDragOver as unknown as EventListener)
      editor.addEventListener('dragleave', handleDragLeave as unknown as EventListener)
      editor.addEventListener('drop', handleDrop as unknown as EventListener)
    }
  }

  function teardown() {
    const editor = document.querySelector(editorSelector)
    if (editor) {
      editor.removeEventListener('paste', handlePaste as unknown as EventListener)
      editor.removeEventListener('dragover', handleDragOver as unknown as EventListener)
      editor.removeEventListener('dragleave', handleDragLeave as unknown as EventListener)
      editor.removeEventListener('drop', handleDrop as unknown as EventListener)
    }
  }

  onMounted(() => {
    // Delay to ensure editor is rendered
    setTimeout(setup, 300)
  })

  onUnmounted(teardown)

  return { uploading }
}
