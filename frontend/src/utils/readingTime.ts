export function calculateReadingTime(content: string): string {
  const cjkChars = (content.match(/[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]/g) || []).length
  const enWords = (content.match(/[a-zA-Z]+/g) || []).length
  const minutes = Math.max(1, Math.round(Math.max(cjkChars / 300, enWords / 200)))
  return `${minutes} min`
}
