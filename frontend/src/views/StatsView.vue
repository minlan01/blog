<template>
  <section class="stats-page">
    <div class="container">
      <header class="stats-page__header">
        <button class="stats-page__back" @click="$router.push('/admin')">&larr; 返回管理</button>
        <span class="stats-page__label">STATISTICS</span>
        <h1 class="stats-page__title">站点统计</h1>
      </header>

      <!-- Overview cards -->
      <div class="stats-page__overview">
        <div class="stats-page__stat-card" v-for="stat in overviewStats" :key="stat.label">
          <div class="stats-page__stat-icon" v-html="stat.icon"></div>
          <div class="stats-page__stat-info">
            <span class="stats-page__stat-value">{{ stat.value }}</span>
            <span class="stats-page__stat-label">{{ stat.label }}</span>
          </div>
        </div>
      </div>

      <!-- Content breakdown -->
      <div class="stats-page__content-stats" v-if="stats">
        <h2 class="stats-page__section-title">内容概况</h2>
        <div class="stats-page__content-grid">
          <div class="stats-page__content-item" v-for="item in contentStats" :key="item.label">
            <span class="stats-page__content-value">{{ item.value }}</span>
            <span class="stats-page__content-label">{{ item.label }}</span>
          </div>
        </div>
      </div>

      <!-- Chart placeholder -->
      <div class="stats-page__chart-section">
        <h2 class="stats-page__section-title">访问趋势</h2>
        <div class="stats-page__chart-placeholder">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
          <span>访问趋势图表区域（可接入 Umami 等统计服务）</span>
        </div>
      </div>

      <div class="stats-page__grid">
        <!-- Top Pages -->
        <div class="stats-page__panel">
          <h2 class="stats-page__section-title">站点页面</h2>
          <table class="stats-page__table">
            <thead>
              <tr>
                <th>路径</th>
                <th>页面</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="page in topPages" :key="page.path">
                <td class="stats-page__table-path">{{ page.path }}</td>
                <td>{{ page.label }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Device breakdown -->
        <div class="stats-page__panel">
          <h2 class="stats-page__section-title">设备分布</h2>
          <div class="stats-page__bars">
            <div v-for="device in devices" :key="device.name" class="stats-page__bar-item">
              <div class="stats-page__bar-header">
                <span class="stats-page__bar-name">{{ device.name }}</span>
                <span class="stats-page__bar-pct">{{ device.pct }}%</span>
              </div>
              <div class="stats-page__bar-track">
                <div class="stats-page__bar-fill" :style="{ width: device.pct + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Browser breakdown -->
        <div class="stats-page__panel">
          <h2 class="stats-page__section-title">浏览器分布</h2>
          <div class="stats-page__bars">
            <div v-for="br in browsers" :key="br.name" class="stats-page__bar-item">
              <div class="stats-page__bar-header">
                <span class="stats-page__bar-name">{{ br.name }}</span>
                <span class="stats-page__bar-pct">{{ br.pct }}%</span>
              </div>
              <div class="stats-page__bar-track">
                <div class="stats-page__bar-fill" :style="{ width: br.pct + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Referrer sources -->
        <div class="stats-page__panel">
          <h2 class="stats-page__section-title">来源分布</h2>
          <table class="stats-page__table">
            <thead>
              <tr>
                <th>来源</th>
                <th>访客</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ref in referrers" :key="ref.source">
                <td>{{ ref.source }}</td>
                <td>{{ ref.visitors }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getStats, type SiteStats } from '@/api/blog'

const stats = ref<SiteStats | null>(null)
const loading = ref(true)

function formatNumber(n: number): string {
  if (n >= 10000) return (n / 10000).toFixed(1) + 'w'
  if (n >= 1000) return n.toLocaleString()
  return String(n)
}

function formatWords(n: number): string {
  if (n >= 10000) return (n / 10000).toFixed(1) + ' 万字'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k 字'
  return n + ' 字'
}

const overviewStats = computed(() => {
  if (!stats.value) return []
  const s = stats.value
  return [
    { label: '文章', value: formatNumber(s.posts), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>' },
    { label: '总浏览', value: formatNumber(s.total_views), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>' },
    { label: '评论', value: formatNumber(s.comments), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>' },
    { label: '总字数', value: formatWords(s.total_words), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' },
  ]
})

const contentStats = computed(() => {
  if (!stats.value) return []
  const s = stats.value
  return [
    { label: '分类', value: s.categories },
    { label: '标签', value: s.tags },
    { label: '留言', value: s.messages },
    { label: '友链', value: s.friend_links },
    { label: '用户', value: s.users },
  ]
})

// Placeholder data for analytics not yet connected
const topPages = [
  { path: '/', label: '首页' },
  { path: '/posts', label: '文章列表' },
  { path: '/about', label: '关于' },
  { path: '/archive', label: '归档' },
  { path: '/link', label: '友链' },
]

const devices = [
  { name: 'Desktop', pct: 58 },
  { name: 'Mobile', pct: 34 },
  { name: 'Tablet', pct: 8 },
]

const browsers = [
  { name: 'Chrome', pct: 62 },
  { name: 'Safari', pct: 18 },
  { name: 'Firefox', pct: 11 },
  { name: 'Edge', pct: 7 },
  { name: 'Other', pct: 2 },
]

const referrers = [
  { source: '直接访问', visitors: 1450 },
  { source: 'Google', visitors: 820 },
  { source: 'GitHub', visitors: 340 },
  { source: 'Bing', visitors: 210 },
  { source: 'Bilibili', visitors: 156 },
]

onMounted(async () => {
  try {
    stats.value = await getStats()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stats-page {
  padding: var(--space-3xl) 0;
}

.stats-page__header {
  margin-bottom: var(--space-xl);
}

.stats-page__back {
  display: inline-block;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-muted);
  background: none;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 6px 14px;
  cursor: pointer;
  margin-bottom: var(--space-md);
  transition: all var(--duration-fast) ease;
}

.stats-page__back:hover {
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.stats-page__label {
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.stats-page__title {
  font-size: clamp(1.6rem, 3.5vw, 2.2rem);
  margin: var(--space-xs) 0;
}

/* Overview cards */
.stats-page__overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-xl);
}

.stats-page__stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: var(--space-lg);
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  transition: border-color var(--duration-fast) ease;
}

.stats-page__stat-card:hover {
  border-color: var(--accent-tint-30);
}

.stats-page__stat-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: var(--accent-tint-10);
  color: var(--color-accent);
  flex-shrink: 0;
}

.stats-page__stat-info {
  display: flex;
  flex-direction: column;
}

.stats-page__stat-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--color-text-heading);
  font-family: var(--font-mono);
}

.stats-page__stat-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

/* Chart */
.stats-page__chart-section {
  margin-bottom: var(--space-xl);
}

/* Content stats */
.stats-page__content-stats {
  margin-bottom: var(--space-xl);
}

.stats-page__content-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--space-md);
}

.stats-page__content-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: var(--space-md);
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
}

.stats-page__content-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-text-heading);
  font-family: var(--font-mono);
}

.stats-page__content-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.stats-page__section-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin-bottom: var(--space-md);
}

.stats-page__chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  height: 200px;
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-card-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.stats-page__chart-placeholder svg {
  opacity: 0.3;
}

/* Panels grid */
.stats-page__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-lg);
}

.stats-page__panel {
  padding: var(--space-lg);
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
}

/* Tables */
.stats-page__table {
  width: 100%;
  border-collapse: collapse;
}

.stats-page__table th {
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
}

.stats-page__table td {
  padding: 10px 0;
  font-size: 0.85rem;
  color: var(--color-text-soft);
  border-bottom: 1px solid var(--color-border);
}

.stats-page__table tr:last-child td {
  border-bottom: none;
}

.stats-page__table-path {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--color-text);
}

/* Bars */
.stats-page__bars {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.stats-page__bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stats-page__bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-page__bar-name {
  font-size: 0.85rem;
  color: var(--color-text);
}

.stats-page__bar-pct {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

.stats-page__bar-track {
  height: 8px;
  background: var(--color-surface);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.stats-page__bar-fill {
  height: 100%;
  background: var(--color-accent-gradient);
  border-radius: var(--radius-full);
  transition: width 0.6s var(--ease-out);
}

@media (max-width: 768px) {
  .stats-page {
    padding: var(--space-xl) 0;
  }

  .stats-page__overview {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-sm);
  }

  .stats-page__content-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .stats-page__stat-card {
    padding: var(--space-md);
    gap: 10px;
  }

  .stats-page__stat-icon {
    width: 36px;
    height: 36px;
  }

  .stats-page__stat-value {
    font-size: 1.1rem;
  }

  .stats-page__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .stats-page__overview {
    grid-template-columns: 1fr;
  }

  .stats-page__chart-placeholder {
    height: 140px;
  }
}
</style>
