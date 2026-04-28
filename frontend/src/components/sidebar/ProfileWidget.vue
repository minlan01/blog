<template>
  <div class="profile-widget">
    <RouterLink to="/about" class="profile-widget__avatar-link">
      <img
        :src="profile?.avatar || '/default-avatar.png'"
        alt="赤夜冥岚"
        class="profile-widget__avatar"
      />
      <div class="profile-widget__avatar-overlay">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      </div>
    </RouterLink>

    <h3 class="profile-widget__name">赤夜冥岚</h3>
    <div class="profile-widget__accent-line"></div>
    <p class="profile-widget__bio">热爱编程与技术的开发者，用文字记录思考与实践。</p>

    <div class="profile-widget__social">
      <a v-if="profile?.github_url" :href="profile.github_url" target="_blank" rel="noopener" class="profile-widget__social-btn" title="GitHub">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
      </a>
      <a href="mailto:746408662@qq.com" class="profile-widget__social-btn" title="Email">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
      </a>
    </div>

    <!-- 公告 -->
    <div class="profile-widget__notice">
      <div class="profile-widget__notice-header">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        <span>公告</span>
      </div>
      <p class="profile-widget__notice-text">{{ profile?.intro_text || '欢迎来到我的博客，这里记录技术与生活的点滴。' }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSiteStore } from '@/stores/site'

const siteStore = useSiteStore()
const profile = computed(() => siteStore.profile)
</script>

<style scoped>
.profile-widget {
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  padding: var(--space-lg);
  box-shadow: var(--glass-card-shadow);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.profile-widget::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--glass-noise-highlight);
  background-size: var(--glass-noise-highlight-size);
  background-repeat: repeat, no-repeat;
  background-position: 0 0, 0 0;
  pointer-events: none;
  z-index: 0;
}

.profile-widget > * {
  position: relative;
  z-index: 1;
}

.profile-widget__avatar-link {
  position: relative;
  display: inline-block;
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: var(--space-md);
}

.profile-widget__avatar {
  width: 120px;
  height: 120px;
  object-fit: cover;
  display: block;
  transition: filter 0.3s ease;
}

.profile-widget__avatar-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  color: #fff;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.profile-widget__avatar-link:hover .profile-widget__avatar-overlay {
  opacity: 1;
}

.profile-widget__name {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-text-heading);
  margin: 0 0 6px;
}

.profile-widget__accent-line {
  width: 20px;
  height: 3px;
  background: var(--color-accent);
  border-radius: 2px;
  margin: 0 auto var(--space-sm);
}

.profile-widget__bio {
  font-size: 0.82rem;
  color: var(--color-text-muted);
  line-height: 1.7;
  margin: 0 0 var(--space-md);
}

.profile-widget__social {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.profile-widget__social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  background: var(--accent-tint-08);
  color: var(--color-text-muted);
  transition: all var(--duration-fast) ease;
}

.profile-widget__social-btn:hover {
  background: var(--accent-tint-15);
  color: var(--color-accent);
}

/* Notice / 公告 */
.profile-widget__notice {
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px dashed var(--border-medium);
  text-align: left;
}

.profile-widget__notice-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
  margin-bottom: 6px;
}

.profile-widget__notice-header svg {
  color: var(--color-ochre);
}

.profile-widget__notice-text {
  font-size: 0.78rem;
  color: var(--color-text-soft);
  line-height: 1.7;
  margin: 0;
}
</style>
