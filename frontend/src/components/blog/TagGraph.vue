<template>
  <div class="tag-graph">
    <canvas ref="canvasRef" class="tag-graph__canvas"></canvas>
    <div v-if="hoveredTag" class="tag-graph__tooltip" :style="tooltipStyle">
      <span class="tag-graph__tooltip-name">{{ hoveredTag.name }}</span>
      <span class="tag-graph__tooltip-count">{{ hoveredTag.count }} 篇文章</span>
    </div>
    <div v-if="!tags.length" class="tag-graph__empty">暂无标签数据</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { Tag } from '@/types/blog'

const props = defineProps<{ tags: Tag[] }>()
const router = useRouter()

interface Node {
  id: number
  name: string
  slug: string
  count: number
  x: number
  y: number
  vx: number
  vy: number
  radius: number
}

interface Edge {
  source: number
  target: number
  weight: number
}

const canvasRef = ref<HTMLCanvasElement | null>(null)
const hoveredTag = ref<(Node & { count: number }) | null>(null)
const tooltipStyle = ref({ left: '0px', top: '0px' })

let nodes: Node[] = []
let edges: Edge[] = []
let animationId = 0
let isDragging = false
let dragNode: Node | null = null
let mouseX = 0
let mouseY = 0

const COLORS = {
  node: getComputedStyle(document.documentElement).getPropertyValue('--color-accent').trim() || '#818cf8',
  nodeHover: getComputedStyle(document.documentElement).getPropertyValue('--color-accent-2').trim() || '#f59e0b',
  edge: 'rgba(129, 140, 248, 0.15)',
  text: getComputedStyle(document.documentElement).getPropertyValue('--color-text-muted').trim() || '#999',
}

function buildGraph() {
  if (!props.tags.length) return

  const W = canvasRef.value?.width || 300
  const H = canvasRef.value?.height || 200

  nodes = props.tags.map((t, i) => {
    const angle = (i / props.tags.length) * Math.PI * 2
    const r = Math.min(W, H) * 0.3
    const count = (t as any).post_count || (t as any).count || 1
    return {
      id: t.id,
      name: t.name,
      slug: t.slug,
      count,
      x: W / 2 + Math.cos(angle) * r,
      y: H / 2 + Math.sin(angle) * r,
      vx: 0,
      vy: 0,
      radius: 12 + Math.min(count * 3, 20),
    }
  })

  // Edges: connect tags that are "related" (simplified — all to center hub if <10 tags)
  edges = []
  if (nodes.length <= 1) return

  // Create edges between high-count tags (simulated co-occurrence)
  const sorted = [...nodes].sort((a, b) => b.count - a.count)
  const hub = sorted[0]
  for (let i = 1; i < sorted.length; i++) {
    edges.push({ source: hub.id, target: sorted[i].id, weight: 1 })
  }
  // A few cross connections for visual richness
  for (let i = 1; i < sorted.length - 1; i += 2) {
    edges.push({ source: sorted[i].id, target: sorted[i + 1].id, weight: 0.5 })
  }
}

function simulate() {
  if (!nodes.length) return

  const W = canvasRef.value?.width || 300
  const H = canvasRef.value?.height || 200
  const cx = W / 2
  const cy = H / 2

  // Repulsion between nodes
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[j].x - nodes[i].x
      const dy = nodes[j].y - nodes[i].y
      const dist = Math.sqrt(dx * dx + dy * dy) || 1
      const force = 800 / (dist * dist)
      const fx = (dx / dist) * force
      const fy = (dy / dist) * force
      nodes[i].vx -= fx
      nodes[i].vy -= fy
      nodes[j].vx += fx
      nodes[j].vy += fy
    }
  }

  // Attraction along edges
  const nodeMap = new Map(nodes.map(n => [n.id, n]))
  for (const edge of edges) {
    const s = nodeMap.get(edge.source)
    const t = nodeMap.get(edge.target)
    if (!s || !t) continue
    const dx = t.x - s.x
    const dy = t.y - s.y
    const dist = Math.sqrt(dx * dx + dy * dy) || 1
    const idealDist = 80
    const force = (dist - idealDist) * 0.01 * edge.weight
    const fx = (dx / dist) * force
    const fy = (dy / dist) * force
    s.vx += fx
    s.vy += fy
    t.vx -= fx
    t.vy -= fy
  }

  // Center gravity
  for (const n of nodes) {
    n.vx += (cx - n.x) * 0.002
    n.vy += (cy - n.y) * 0.002
  }

  // Update positions with damping
  for (const n of nodes) {
    if (n === dragNode) continue
    n.vx *= 0.85
    n.vy *= 0.85
    n.x += n.vx
    n.y += n.vy

    // Bounds
    n.x = Math.max(n.radius, Math.min(W - n.radius, n.x))
    n.y = Math.max(n.radius, Math.min(H - n.radius, n.y))
  }
}

function draw() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const W = canvas.width
  const H = canvas.height
  ctx.clearRect(0, 0, W, H)

  // Draw edges
  ctx.strokeStyle = COLORS.edge
  ctx.lineWidth = 1
  const nodeMap = new Map(nodes.map(n => [n.id, n]))
  for (const edge of edges) {
    const s = nodeMap.get(edge.source)
    const t = nodeMap.get(edge.target)
    if (!s || !t) continue
    ctx.globalAlpha = edge.weight * 0.5 + 0.1
    ctx.beginPath()
    ctx.moveTo(s.x, s.y)
    ctx.lineTo(t.x, t.y)
    ctx.stroke()
  }
  ctx.globalAlpha = 1

  // Draw nodes
  for (const n of nodes) {
    const isHovered = hoveredTag.value?.id === n.id
    ctx.beginPath()
    ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2)
    ctx.fillStyle = isHovered ? COLORS.nodeHover : COLORS.node
    ctx.globalAlpha = 0.2 + Math.min(n.count / 10, 0.6)
    ctx.fill()
    ctx.globalAlpha = 1
    ctx.strokeStyle = isHovered ? COLORS.nodeHover : COLORS.node
    ctx.lineWidth = 1.5
    ctx.stroke()

    // Label
    ctx.fillStyle = COLORS.text
    ctx.font = `${Math.min(10 + n.count, 14)}px Inter, sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(n.name, n.x, n.y)
  }
}

function loop() {
  simulate()
  draw()
  animationId = requestAnimationFrame(loop)
}

function findNodeAt(x: number, y: number): Node | null {
  for (const n of nodes) {
    const dx = n.x - x
    const dy = n.y - y
    if (Math.sqrt(dx * dx + dy * dy) < n.radius) return n
  }
  return null
}

function onMouseMove(e: MouseEvent) {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  mouseX = (e.clientX - rect.left) * (canvas.width / rect.width)
  mouseY = (e.clientY - rect.top) * (canvas.height / rect.height)

  if (isDragging && dragNode) {
    dragNode.x = mouseX
    dragNode.y = mouseY
    dragNode.vx = 0
    dragNode.vy = 0
    return
  }

  const found = findNodeAt(mouseX, mouseY)
  if (found) {
    hoveredTag.value = found
    tooltipStyle.value = {
      left: `${e.clientX - rect.left + 12}px`,
      top: `${e.clientY - rect.top - 30}px`,
    }
    canvas.style.cursor = 'pointer'
  } else {
    hoveredTag.value = null
    canvas.style.cursor = isDragging ? 'grabbing' : 'default'
  }
}

function onMouseDown(e: MouseEvent) {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const x = (e.clientX - rect.left) * (canvas.width / rect.width)
  const y = (e.clientY - rect.top) * (canvas.height / rect.height)
  const found = findNodeAt(x, y)
  if (found) {
    isDragging = true
    dragNode = found
    canvas.style.cursor = 'grabbing'
  }
}

function onMouseUp() {
  if (dragNode && !isDragging) {
    // Treat as click
    router.push(`/posts?tag=${dragNode.slug}`)
  }
  isDragging = false
  dragNode = null
}

function onMouseLeave() {
  isDragging = false
  dragNode = null
  hoveredTag.value = null
}

function resizeCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return
  const parent = canvas.parentElement
  if (!parent) return
  const dpr = window.devicePixelRatio || 1
  const w = parent.clientWidth
  const h = parent.clientHeight
  canvas.width = w * dpr
  canvas.height = h * dpr
  canvas.style.width = `${w}px`
  canvas.style.height = `${h}px`
  const ctx = canvas.getContext('2d')
  if (ctx) ctx.scale(dpr, dpr)
  // Rebuild nodes for new dimensions
  buildGraph()
}

onMounted(() => {
  resizeCanvas()
  loop()

  const canvas = canvasRef.value
  if (canvas) {
    canvas.addEventListener('mousemove', onMouseMove)
    canvas.addEventListener('mousedown', onMouseDown)
    canvas.addEventListener('mouseup', onMouseUp)
    canvas.addEventListener('mouseleave', onMouseLeave)
  }
  window.addEventListener('resize', resizeCanvas)
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  const canvas = canvasRef.value
  if (canvas) {
    canvas.removeEventListener('mousemove', onMouseMove)
    canvas.removeEventListener('mousedown', onMouseDown)
    canvas.removeEventListener('mouseup', onMouseUp)
    canvas.removeEventListener('mouseleave', onMouseLeave)
  }
  window.removeEventListener('resize', resizeCanvas)
})

watch(() => props.tags, () => {
  buildGraph()
}, { deep: true })
</script>

<style scoped>
.tag-graph {
  position: relative;
  width: 100%;
  height: 280px;
  overflow: hidden;
}

.tag-graph__canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.tag-graph__tooltip {
  position: absolute;
  pointer-events: none;
  background: rgba(15, 15, 30, 0.95);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  font-size: 0.78rem;
  display: flex;
  flex-direction: column;
  gap: 2px;
  z-index: 10;
}

.tag-graph__tooltip-name {
  font-weight: 600;
  color: var(--color-accent);
}

.tag-graph__tooltip-count {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

.tag-graph__empty {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  font-size: 0.85rem;
}
</style>
