import { ref } from 'vue'
import { http } from '@/api/http'

export function useImageUpload() {
  const uploading = ref(false)

  async function uploadImage(file: File): Promise<string | null> {
    if (!file.type.startsWith('image/')) return null
    uploading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await http.post<{ url: string; filename: string }>('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 0,
      })
      return data.url.startsWith('http') ? data.url : `/api/v1${data.url}`
    } catch {
      return null
    } finally {
      uploading.value = false
    }
  }

  async function uploadMedia(file: File): Promise<{ url: string; mediaType: string } | null> {
    uploading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await http.post<{ url: string; filename: string; media_type: string }>('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 0,
      })
      const url = data.url.startsWith('http') ? data.url : `/api/v1${data.url}`
      return { url, mediaType: data.media_type || 'image' }
    } catch {
      return null
    } finally {
      uploading.value = false
    }
  }

  return { uploading, uploadImage, uploadMedia }
}
