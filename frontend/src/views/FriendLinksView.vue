<template>
  <section class="links-page">
    <div class="container">
      <header class="links-page__header">
        <span class="links-page__label">LINKS</span>
        <h1 class="links-page__title">友情链接</h1>
      </header>

      <!-- Action buttons -->
      <div class="links-page__actions">
        <button class="links-page__action-btn" @click="randomVisit">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg>
          随机访问
        </button>
      </div>

      <!-- Link sections -->
      <div v-for="section in linkSections" :key="section.title" class="links-page__section">
        <h2 class="links-page__section-title">{{ section.title }}</h2>
        <div class="links-page__grid">
          <a
            v-for="link in section.links"
            :key="link.name"
            :href="link.url"
            target="_blank"
            rel="noopener"
            class="links-page__card"
          >
            <img
              v-if="link.avatar"
              :src="link.avatar"
              :alt="link.name"
              class="links-page__avatar"
            />
            <div v-else class="links-page__avatar-placeholder">
              {{ link.name.charAt(0) }}
            </div>
            <div class="links-page__info">
              <div class="links-page__name-wrap">
                <span class="links-page__name">{{ link.name }}</span>
                <span v-if="link.badge" class="links-page__badge">{{ link.badge }}</span>
              </div>
              <span class="links-page__desc">{{ link.description }}</span>
            </div>
          </a>
        </div>
      </div>

      <!-- Apply section -->
      <div class="links-page__apply">
        <h2 class="links-page__section-title">申请友链</h2>
        <div class="links-page__apply-content">
          <div class="links-page__apply-rules">
            <h3>申请要求</h3>
            <ul>
              <li>站点必须支持 HTTPS</li>
              <li>站点内容合法合规，无不良信息</li>
              <li>站点能够正常访问，持续维护</li>
              <li>优先考虑原创技术博客</li>
            </ul>
          </div>
          <div class="links-page__apply-info">
            <h3>本站信息</h3>
            <div class="links-page__info-card">
              <div class="links-page__info-row">
                <span class="links-page__info-label">名称</span>
                <span class="links-page__info-value">{{ profile?.site_name || '赤夜冥岚' }}</span>
              </div>
              <div class="links-page__info-row">
                <span class="links-page__info-label">描述</span>
                <span class="links-page__info-value">{{ profile?.intro_text || '一个技术博客' }}</span>
              </div>
              <div class="links-page__info-row">
                <span class="links-page__info-label">地址</span>
                <span class="links-page__info-value">{{ siteUrl }}</span>
              </div>
              <div class="links-page__info-row">
                <span class="links-page__info-label">头像</span>
                <span class="links-page__info-value">{{ profile?.avatar || '联系获取' }}</span>
              </div>
            </div>
            <p class="links-page__apply-note">请在留言板或通过邮件提交您的站点信息</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useSiteStore } from '@/stores/site'
import { getFriendLinks } from '@/api/blog'
import type { FriendLink } from '@/types/blog'

const siteStore = useSiteStore()
const profile = computed(() => siteStore.profile)
const siteUrl = ref(window.location.origin)

const links = ref<FriendLink[]>([])
const loading = ref(true)

interface LinkSection {
  title: string
  links: FriendLink[]
}

const linkSections = computed(() => {
  const groups: Record<string, FriendLink[]> = {}
  for (const link of links.value) {
    const cat = link.category || '其他'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(link)
  }
  return Object.entries(groups).map(([title, items]) => ({
    title,
    links: items,
  }))
})

const allLinks = computed(() => links.value.filter((l) => l.url !== '#'))

function randomVisit() {
  if (!allLinks.value.length) return
  const pick = allLinks.value[Math.floor(Math.random() * allLinks.value.length)]
  window.open(pick.url, '_blank', 'noopener')
}

onMounted(async () => {
  if (!siteStore.profile) siteStore.loadProfile()
  try {
    links.value = await getFriendLinks()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.links-page {
  padding: var(--space-3xl) 0;
}

.links-page__header {
  margin-bottom: var(--space-xl);
}

.links-page__label {
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.links-page__title {
  font-size: clamp(1.6rem, 3.5vw, 2.2rem);
  margin: var(--space-xs) 0;
}

/* Actions */
.links-page__actions {
  margin-bottom: var(--space-xl);
}

.links-page__action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-card-blur);
  color: var(--color-text);
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.links-page__action-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: var(--accent-tint-08);
}

.links-page__action-btn svg {
  color: var(--color-accent);
}

/* Sections */
.links-page__section {
  margin-bottom: var(--space-xl);
}

.links-page__section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin-bottom: var(--space-md);
  padding-left: 12px;
  border-left: 3px solid var(--color-accent);
}

/* Grid */
.links-page__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(280px, 100%), 1fr));
  gap: var(--space-md);
}

/* Card */
.links-page__card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--color-text);
  transition: all var(--duration-fast) ease;
  position: relative;
  overflow: hidden;
}

.links-page__card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--glass-noise);
  background-size: 128px 128px;
  pointer-events: none;
  opacity: 0.5;
}

.links-page__card:hover {
  border-color: var(--accent-tint-30);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.links-page__avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  border: 2px solid var(--glass-border);
}

.links-page__avatar-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.links-page__info {
  min-width: 0;
  flex: 1;
  position: relative;
  z-index: 1;
}

.links-page__name-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.links-page__name {
  font-weight: 600;
  font-size: 0.92rem;
  color: var(--color-text-heading);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.links-page__badge {
  font-size: 0.65rem;
  padding: 1px 8px;
  border-radius: var(--radius-full);
  background: var(--accent-tint-15);
  color: var(--color-accent);
  flex-shrink: 0;
}

.links-page__desc {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Apply section */
.links-page__apply {
  margin-top: var(--space-2xl);
  padding: var(--space-xl);
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  position: relative;
}

.links-page__apply::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--glass-noise);
  background-size: 128px 128px;
  pointer-events: none;
}

.links-page__apply-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xl);
  position: relative;
  z-index: 1;
}

.links-page__apply h3 {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin-bottom: var(--space-sm);
}

.links-page__apply-rules ul {
  list-style: none;
  padding: 0;
}

.links-page__apply-rules li {
  padding: 6px 0;
  font-size: 0.85rem;
  color: var(--color-text-soft);
  position: relative;
  padding-left: 16px;
}

.links-page__apply-rules li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent);
  transform: translateY(-50%);
}

.links-page__info-card {
  padding: var(--space-md);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border);
}

.links-page__info-row {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.85rem;
}

.links-page__info-row:last-child {
  border-bottom: none;
}

.links-page__info-label {
  color: var(--color-text-muted);
  min-width: 48px;
  flex-shrink: 0;
}

.links-page__info-value {
  color: var(--color-text);
  word-break: break-all;
}

.links-page__apply-note {
  margin-top: var(--space-md);
  font-size: 0.82rem;
  color: var(--color-text-muted);
  text-align: center;
}

@media (max-width: 768px) {
  .links-page {
    padding: var(--space-xl) 0;
  }

  .links-page__grid {
    grid-template-columns: 1fr;
  }

  .links-page__apply-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .links-page__card {
    padding: 12px 14px;
  }

  .links-page__avatar {
    width: 40px;
    height: 40px;
  }

  .links-page__avatar-placeholder {
    width: 40px;
    height: 40px;
    font-size: 0.95rem;
  }
}
</style>
