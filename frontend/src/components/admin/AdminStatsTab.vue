<template>
  <div class="admin-page__panel">
    <div class="admin-page__stats-header">
      <p class="admin-page__stats-desc">站点访问数据分析（可接入 Umami 等统计服务）</p>
      <RouterLink to="/stats" class="admin-page__stats-link">
        查看完整统计 &rarr;
      </RouterLink>
    </div>

    <div class="admin-page__stats-overview">
      <div class="admin-page__stat-card" v-for="stat in statsOverview" :key="stat.label">
        <div class="admin-page__stat-icon" v-html="stat.icon"></div>
        <div class="admin-page__stat-info">
          <span class="admin-page__stat-value">{{ stat.value }}</span>
          <span class="admin-page__stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>

    <div class="admin-page__stats-grid">
      <div class="admin-page__stats-panel">
        <h3 class="admin-page__stats-title">站点页面</h3>
        <table class="admin-table">
          <thead>
            <tr><th>路径</th><th>页面</th></tr>
          </thead>
          <tbody>
            <tr v-for="p in statsTopPages" :key="p.path">
              <td style="font-family:var(--font-mono);font-size:0.82rem;">{{ p.path }}</td>
              <td>{{ p.label }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="admin-page__stats-panel">
        <h3 class="admin-page__stats-title">设备分布</h3>
        <div class="admin-page__bars">
          <div v-for="d in statsDevices" :key="d.name" class="admin-page__bar-item">
            <div class="admin-page__bar-header">
              <span>{{ d.name }}</span>
              <span style="font-family:var(--font-mono);font-size:0.78rem;color:var(--color-text-muted);">{{ d.pct }}%</span>
            </div>
            <div class="admin-page__bar-track">
              <div class="admin-page__bar-fill" :style="{ width: d.pct + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { getStats, type SiteStats } from '@/api/blog'
import { safeCall } from '@/api/http'

const siteStats = ref<SiteStats | null>(null)

const statsOverview = computed(() => {
  if (!siteStats.value) return []
  const s = siteStats.value
  return [
    { label: '文章', value: String(s.posts), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>' },
    { label: '总浏览', value: s.total_views.toLocaleString(), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>' },
    { label: '评论', value: String(s.comments), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>' },
    { label: '留言', value: String(s.messages), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
  ]
})

const statsTopPages = [
  { path: '/', label: '首页' },
  { path: '/posts', label: '文章' },
  { path: '/about', label: '关于' },
  { path: '/archive', label: '归档' },
]
const statsDevices = [
  { name: 'Desktop', pct: 58 },
  { name: 'Mobile', pct: 34 },
  { name: 'Tablet', pct: 8 },
]

async function loadStats() {
  siteStats.value = await safeCall(() => getStats(), null as unknown as SiteStats)
}

loadStats()
</script>

<style scoped>
.admin-page__stats-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
}

.admin-page__stats-desc {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.admin-page__stats-link {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-accent);
  text-decoration: none;
  transition: opacity var(--duration-fast) ease;
}

.admin-page__stats-link:hover {
  opacity: 0.75;
}

.admin-page__stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.admin-page__stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: var(--space-md);
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
}

.admin-page__stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  background: var(--accent-tint-10);
  color: var(--color-accent);
  flex-shrink: 0;
}

.admin-page__stat-info {
  display: flex;
  flex-direction: column;
}

.admin-page__stat-value {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-text-heading);
  font-family: var(--font-mono);
}

.admin-page__stat-label {
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

.admin-page__stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-lg);
}

.admin-page__stats-panel {
  padding: var(--space-md);
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
}

.admin-page__stats-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin: 0 0 var(--space-md);
}

.admin-page__bars {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.admin-page__bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.admin-page__bar-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--color-text);
}

.admin-page__bar-track {
  height: 8px;
  background: var(--color-surface-hover);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.admin-page__bar-fill {
  height: 100%;
  background: var(--color-accent-gradient);
  border-radius: var(--radius-full);
}

@media (max-width: 768px) {
  .admin-page__stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }

  .admin-page__stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
