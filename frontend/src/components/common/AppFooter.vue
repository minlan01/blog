<template>
  <footer class="footer">
    <div class="footer__divider-line"></div>
    <div class="footer__inner">
      <!-- Tech badges -->
      <div class="footer__badges">
        <span class="footer__badge">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
          Vue 3
        </span>
        <span class="footer__badge">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
          FastAPI
        </span>
        <span class="footer__badge">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
          Vite
        </span>
        <span class="footer__badge">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>
          TypeScript
        </span>
      </div>

      <!-- Project credit -->
      <div class="footer__credit">
        <span class="footer__credit-name">赤夜冥岚的编程小屋</span>
        <span class="footer__credit-desc">基于 Vue 3 + FastAPI + TypeScript + Vite 构建的个人博客系统</span>
      </div>

      <!-- Links -->
      <div class="footer__content">
        <span class="footer__copy">&copy; {{ year }} {{ brandName }}</span>
        <span class="footer__sep">/</span>
        <RouterLink to="/about" class="footer__link">关于</RouterLink>
        <span class="footer__sep">/</span>
        <a v-if="profile?.github_url" :href="profile.github_url" target="_blank" rel="noopener" class="footer__link">GitHub</a>
        <template v-if="profile?.github_url">
          <span class="footer__sep">/</span>
        </template>
        <a href="mailto:746408662@qq.com" class="footer__link">Email</a>
      </div>

      <!-- Stats bar -->
      <div class="footer__stats">
        <span class="footer__stat">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          文章 {{ siteStore.postCount }}
        </span>
        <span class="footer__stat-dot"></span>
        <span class="footer__stat">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
          标签 {{ siteStore.tagCount }}
        </span>
        <span class="footer__stat-dot"></span>
        <span class="footer__stat">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          分类 {{ siteStore.categoryCount }}
        </span>
      </div>

      <!-- ICP Filing (reserved — set window.__ICP_FILING__ to display) -->
      <div v-if="icpFiling" class="footer__icp">
        <a v-if="icpLink" :href="icpLink" target="_blank" rel="noopener" class="footer__icp-link">{{ icpFiling }}</a>
        <span v-else>{{ icpFiling }}</span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSiteStore } from '@/stores/site'

const siteStore = useSiteStore()
const profile = computed(() => siteStore.profile)
const brandName = computed(() => profile.value?.site_name ?? '赤夜冥岚')
const year = new Date().getFullYear()

// ICP Filing — configurable via site config or global variable
// Set in backend site_config: { icp_filing: "京ICP备xxxxxxx号", icp_link: "https://beian.miit.gov.cn/" }
// Or set at runtime: (window as any).__ICP_FILING__ = "京ICP备xxxxxxx号"
const icpFiling = computed(() => {
  const w = window as any
  return profile.value?.icp_filing || w.__ICP_FILING__ || ''
})
const icpLink = computed(() => {
  const w = window as any
  return profile.value?.icp_link || w.__ICP_LINK__ || ''
})
</script>

<style scoped>
.footer {
  margin-top: var(--space-2xl);
  padding: 0 var(--space-lg);
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  border-top: 1px solid var(--glass-border);
  box-shadow: var(--glass-highlight);
}

.footer__divider-line {
  display: none;
}

.footer__inner {
  max-width: var(--content-width);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg) 0 var(--space-2xl);
  gap: 16px;
}

/* Tech badges */
.footer__badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.footer__badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.7rem;
  font-family: var(--font-mono);
  color: var(--color-text-muted);
  padding: 4px 12px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  background: var(--glass-bg-02);
  letter-spacing: 0.02em;
}

.footer__badge svg {
  opacity: 0.5;
  color: var(--color-accent);
}

/* Links */
.footer__content {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.footer__copy {
  color: var(--color-text-muted);
}

.footer__sep {
  margin: 0 8px;
  opacity: 0.3;
}

.footer__link {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 500;
  transition: opacity var(--duration-fast) ease;
}

.footer__link:hover {
  opacity: 0.75;
}

/* Stats bar */
.footer__stats {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

.footer__stat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-mono);
}

.footer__stat svg {
  opacity: 0.4;
}

.footer__stat-dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--color-text-muted);
  opacity: 0.3;
}

/* Project credit */
.footer__credit {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.footer__credit-name {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-text-heading);
  letter-spacing: 0.03em;
}

.footer__credit-desc {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

/* ICP Filing */
.footer__icp {
  margin-top: var(--space-xs);
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

.footer__icp-link {
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color var(--duration-fast) ease;
}

.footer__icp-link:hover {
  color: var(--color-accent);
}

@media (max-width: 640px) {
  .footer {
    padding: 0 var(--space-md);
  }

  .footer__badges {
    gap: 6px;
  }
}
</style>
