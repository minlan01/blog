<template>
  <section class="about">
    <div class="container narrow-container">

      <!-- Hero Banner -->
      <div class="about__hero">
        <div class="about__hero-glow"></div>
        <div class="about__hero-content">
          <div class="about__hero-avatar-wrap">
            <img
              :src="profile?.avatar || '/default-avatar.png'"
              alt="赤夜冥岚"
              class="about__hero-avatar"
            />
            <span class="about__hero-badge">ONLINE</span>
          </div>
          <div class="about__hero-info">
            <span class="about__hero-kicker">ABOUT</span>
            <h1 class="about__hero-name">赤夜冥岚</h1>
            <p class="about__hero-role">
              <span class="about__hero-role-tag">Developer</span>
              <span class="about__hero-role-sep">&</span>
              <span class="about__hero-role-tag">Writer</span>
            </p>
          </div>
        </div>
        <div class="about__hero-border"></div>
      </div>

      <!-- 故事区 -->
      <div class="about__story">
        <div class="about__section-label">
          <span class="about__section-num">01</span>
          <span class="about__section-title">关于我</span>
        </div>
        <div class="about__story-text">
          <p>
            你好，我是赤夜冥岚，一名来自中国云南的开发者。热爱编程、热爱技术，也热爱把思考写下来这件事。
          </p>
          <p>
            这个博客是我的个人技术空间，用来记录学习过程中的思考、实践中踩过的坑，以及一些值得分享的经验。
            我相信写下来是最好的学习方式，每一篇文章都是对知识的梳理与沉淀。
          </p>
          <p>
            如果你在这里找到了有用的内容，那就是这个博客存在的意义。
          </p>
        </div>
      </div>

      <!-- 分隔线 -->
      <div class="about__divider"></div>

      <!-- 联系方式 -->
      <div class="about__contact">
        <div class="about__section-label">
          <span class="about__section-num">02</span>
          <span class="about__section-title">联系方式</span>
        </div>
        <div class="about__contact-grid">
          <div class="about__contact-item">
            <div class="about__contact-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            </div>
            <div class="about__contact-info">
              <span class="about__contact-label">EMAIL</span>
              <a href="mailto:746408662@qq.com" class="about__contact-value">746408662@qq.com</a>
            </div>
          </div>

          <div class="about__contact-item" v-if="profile?.github_url">
            <div class="about__contact-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
            </div>
            <div class="about__contact-info">
              <span class="about__contact-label">GITHUB</span>
              <a :href="profile.github_url" target="_blank" rel="noopener" class="about__contact-value">
                {{ profile.github_url.replace('https://github.com/', '') }}
              </a>
            </div>
          </div>

          <div class="about__contact-item">
            <div class="about__contact-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            </div>
            <div class="about__contact-info">
              <span class="about__contact-label">LOCATION</span>
              <span class="about__contact-value about__contact-static">中国云南</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 分隔线 -->
      <div class="about__divider"></div>

      <!-- 技术栈 -->
      <div class="about__stack">
        <div class="about__section-label">
          <span class="about__section-num">03</span>
          <span class="about__section-title">技术栈</span>
        </div>
        <p class="about__stack-desc">本博客项目使用以下技术构建</p>
        <div class="about__stack-grid">
          <div v-for="item in techStack" :key="item.name" class="about__stack-badge">
            <span class="about__stack-badge-icon" v-html="item.svg"></span>
            <span class="about__stack-badge-name">{{ item.name }}</span>
          </div>
        </div>
      </div>

      <!-- 分隔线 -->
      <div class="about__divider"></div>

      <!-- 关于项目 -->
      <div class="about__project">
        <div class="about__section-label">
          <span class="about__section-num">04</span>
          <span class="about__section-title">关于项目</span>
        </div>
        <div class="about__project-text">
          <p>
            这是一个基于 <strong>Vue 3 + FastAPI</strong> 的前后端分离个人博客系统。前端以视觉体验与交互细节为核心，后端提供稳定的 API 接口与数据管理能力。
          </p>
          <p>
            前端采用 <strong>Vue 3 Composition API</strong> 与 <strong>TypeScript</strong> 开发，通过 Vite 构建，使用 Pinia 管理全局状态。界面延续毛玻璃深色主题风格，注重阅读体验与响应式适配。
          </p>
          <p>
            后端使用 <strong>FastAPI</strong> 框架，结合 SQLAlchemy ORM 与 SQLite 数据库，以 Pydantic 进行数据校验。整体架构轻量、高效，适合个人博客场景。
          </p>
        </div>
      </div>

      <!-- 底部留白 -->
      <div class="about__footer">
        <span class="about__footer-line">// Thanks for visiting.</span>
      </div>

    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useSiteStore } from '@/stores/site'

const siteStore = useSiteStore()
const profile = computed(() => siteStore.profile)

const techStack = [
  { name: 'Vue 3', svg: '<svg viewBox="0 0 256 221" width="20" height="18" fill="none"><path d="M204.8 0H256L128 220.8 0 0h97.9L128 51.2 157.9 0h46.9z" fill="#818cf8"/><path d="M0 0l128 220.8L256 0h-51.2L128 132.5 50.6 0H0z" fill="rgba(129,140,248,0.35)"/></svg>' },
  { name: 'TypeScript', svg: '<svg viewBox="0 0 256 256" width="18" height="18"><rect width="256" height="256" rx="20" fill="rgba(129,140,248,0.1)"/><path d="M150 180h-28v-80h-20v-20h68v20h-20v80z" fill="#818cf8"/><rect x="88" y="116" width="16" height="64" fill="rgba(129,140,248,0.5)"/></svg>' },
  { name: 'Vite', svg: '<svg viewBox="0 0 256 257" width="18" height="18"><path d="M128 4L8 44l18 160 102 49 102-49 18-160L128 4z" fill="rgba(129,140,248,0.08)"/><path d="M128 4v249l-102-49L8 44 128 4z" fill="rgba(129,140,248,0.15)"/><path d="M128 30l76 170H162l-18-42h-32l-18 42H52L128 30z" fill="#818cf8"/></svg>' },
  { name: 'Pinia', svg: '<svg viewBox="0 0 256 283" width="18" height="20"><path d="M128 40c-30 0-55 28-55 62 0 20 9 38 22 49v28l33 34 33-34v-28c13-11 22-29 22-49 0-34-25-62-55-62z" fill="rgba(129,140,248,0.2)" stroke="#818cf8" stroke-width="6"/><circle cx="113" cy="88" r="6" fill="#818cf8"/><circle cx="143" cy="88" r="6" fill="#818cf8"/></svg>' },
  { name: 'Python', svg: '<svg viewBox="0 0 256 255" width="18" height="18"><path d="M126.9 0C62.8 0 66.3 28 66.3 28l.1 29h62v9H39S0 61 0 127c0 66 34 64 34 64h20v-31s-1-35 34-35h59s33 .5 33-32v-61S183 0 126.9 0zM93 18a10 10 0 110 20 10 10 0 010-20z" fill="rgba(129,140,248,0.4)"/><path d="M129 255c64 0 60.5-28 60.5-28l-.1-29h-62v-9h89.4s38.7 5 38.7-61c0-66-34-64-34-64h-20v31s1 35-34 35h-59s-33-.5-33 32v61S72.8 255 129 255zm34-18a10 10 0 110-20 10 10 0 010 20z" fill="#818cf8"/></svg>' },
  { name: 'FastAPI', svg: '<svg viewBox="0 0 256 221" width="20" height="18"><path d="M0 0l128 220.8L256 0H0z" fill="rgba(129,140,248,0.06)"/><path d="M110 60h36v12h-36V60zm0 30h80v12h-80V90zm0 30h100v12H110V120zm0 30h60v12h-60v-12z" fill="#818cf8"/></svg>' },
  { name: 'SQLAlchemy', svg: '<svg viewBox="0 0 256 256" width="18" height="18"><ellipse cx="128" cy="60" rx="80" ry="30" fill="none" stroke="#818cf8" stroke-width="6"/><path d="M48 60v68c0 16.5 35.8 30 80 30s80-13.5 80-30V60" fill="none" stroke="rgba(129,140,248,0.5)" stroke-width="6"/><path d="M48 128v68c0 16.5 35.8 30 80 30s80-13.5 80-30v-68" fill="none" stroke="#818cf8" stroke-width="6"/></svg>' },
  { name: 'SQLite', svg: '<svg viewBox="0 0 256 256" width="18" height="18"><path d="M48 20h120l60 60v156c0 11-9 20-20 20H48c-11 0-20-9-20-20V40c0-11 9-20 20-20z" fill="rgba(129,140,248,0.1)" stroke="#818cf8" stroke-width="4"/><path d="M168 20v60h60" fill="none" stroke="rgba(129,140,248,0.4)" stroke-width="4"/><text x="128" y="170" text-anchor="middle" font-size="48" font-weight="bold" fill="#818cf8" font-family="monospace">SQL</text></svg>' },
  { name: 'Vue Router', svg: '<svg viewBox="0 0 256 256" width="18" height="18"><circle cx="128" cy="128" r="90" fill="none" stroke="rgba(129,140,248,0.3)" stroke-width="6"/><path d="M100 88l60 40-60 40V88z" fill="#818cf8"/></svg>' },
  { name: 'Axios', svg: '<svg viewBox="0 0 256 256" width="18" height="18"><path d="M128 30L30 226h46l52-108 52 108h46L128 30z" fill="rgba(129,140,248,0.5)"/><path d="M128 80l-40 146h30l10-30 10 30h30L128 80z" fill="#818cf8"/></svg>' },
]

onMounted(() => siteStore.loadProfile())
</script>

<style scoped>
.about {
  padding: var(--space-3xl) 0;
}

/* ========================================
   Hero Banner
   ======================================== */

.about__hero {
  position: relative;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-card-saturate));
  padding: var(--space-2xl);
  margin-bottom: var(--space-2xl);
  box-shadow: var(--glass-card-shadow);
  overflow: hidden;
}

.about__hero-glow {
  position: absolute;
  top: -40px;
  right: -40px;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, var(--accent-tint-15), transparent 70%);
  pointer-events: none;
}

.about__hero-border {
  position: absolute;
  bottom: 0;
  left: 10%;
  right: 10%;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--accent-tint-30) 30%,
    var(--accent-tint-50),
    var(--accent-tint-30) 70%,
    transparent
  );
}

.about__hero-content {
  display: flex;
  align-items: center;
  gap: var(--space-xl);
  position: relative;
}

.about__hero-avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.about__hero-avatar {
  width: 110px;
  height: 110px;
  border-radius: var(--radius-xl);
  object-fit: cover;
  border: 2px solid var(--border-strong);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
}

.about__hero-badge {
  position: absolute;
  bottom: -6px;
  right: -6px;
  font-family: var(--font-mono);
  font-size: 0.58rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  padding: 3px 8px;
  border-radius: var(--radius-full);
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.3);
  box-shadow: 0 0 12px rgba(52, 211, 153, 0.2);
}

.about__hero-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.about__hero-kicker {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.2em;
  color: var(--color-accent);
  text-transform: uppercase;
}

.about__hero-name {
  font-size: clamp(2rem, 5vw, 2.8rem);
  font-weight: 700;
  margin: 0;
  color: var(--color-text-heading);
  letter-spacing: -0.03em;
  line-height: 1.1;
}

.about__hero-role {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  margin-top: 4px;
}

.about__hero-role-tag {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--color-text-muted);
  letter-spacing: 0.04em;
}

.about__hero-role-sep {
  color: var(--color-accent);
  font-weight: 300;
  font-size: 0.9rem;
}

/* ========================================
   Section Labels
   ======================================== */

.about__section-label {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.about__section-num {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--color-accent);
  letter-spacing: 0.05em;
  padding: 2px 8px;
  border: 1px solid var(--accent-tint-20);
  border-radius: var(--radius-sm);
  background: var(--accent-tint-06);
}

.about__section-title {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-text-heading);
  letter-spacing: -0.01em;
}

/* ========================================
   Story
   ======================================== */

.about__story {
  margin-bottom: var(--space-2xl);
}

.about__story-text p {
  color: var(--color-text-soft);
  line-height: 1.9;
  margin: 0 0 var(--space-md);
  font-size: 0.92rem;
}

.about__story-text p:last-child {
  margin-bottom: 0;
}

/* ========================================
   Divider
   ======================================== */

.about__divider {
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--border-default) 20%,
    var(--border-default) 80%,
    transparent
  );
  margin-bottom: var(--space-2xl);
}

/* ========================================
   Contact
   ======================================== */

.about__contact {
  margin-bottom: var(--space-2xl);
}

.about__contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
}

.about__contact-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: 14px 18px;
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  background: var(--glass-surface-bg);
  backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
  -webkit-backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
  transition: all var(--duration-fast) ease;
}

.about__contact-item:hover {
  border-color: var(--border-strong);
  background: var(--glass-bg-12);
}

.about__contact-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: var(--accent-tint-08);
  color: var(--color-accent);
  flex-shrink: 0;
}

.about__contact-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.about__contact-label {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--color-text-muted);
  text-transform: uppercase;
}

.about__contact-value {
  font-size: 0.85rem;
  color: var(--color-accent);
  word-break: break-all;
  text-decoration: none;
  transition: opacity 0.2s ease;
}

.about__contact-value:hover {
  opacity: 0.8;
}

.about__contact-static {
  color: var(--color-text-soft);
}

/* ========================================
   Tech Stack
   ======================================== */

.about__stack {
  margin-bottom: var(--space-2xl);
}

.about__stack-desc {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin: 0 0 var(--space-lg);
  line-height: 1.6;
}

.about__stack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}

.about__stack-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 18px 12px;
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  background: var(--glass-surface-bg);
  backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
  -webkit-backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
  transition: all var(--duration-fast) ease;
}

.about__stack-badge:hover {
  border-color: var(--accent-tint-20);
  background: var(--accent-tint-04);
  transform: translateY(-2px);
}

.about__stack-badge-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.about__stack-badge-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-text-soft);
  letter-spacing: 0.02em;
}

/* ========================================
   Project
   ======================================== */

.about__project {
  margin-bottom: var(--space-2xl);
}

.about__project-text p {
  color: var(--color-text-soft);
  line-height: 1.9;
  margin: 0 0 var(--space-md);
  font-size: 0.92rem;
}

.about__project-text p:last-child {
  margin-bottom: 0;
}

.about__project-text strong {
  color: var(--color-accent);
  font-weight: 600;
}

/* ========================================
   Footer
   ======================================== */

.about__footer {
  text-align: center;
  padding: var(--space-lg) 0;
}

.about__footer-line {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--color-text-muted);
  opacity: 0.5;
  letter-spacing: 0.03em;
}

/* ========================================
   Responsive
   ======================================== */

@media (max-width: 640px) {
  .about__hero-content {
    flex-direction: column;
    text-align: center;
  }

  .about__hero-role {
    justify-content: center;
  }

  .about__contact-grid {
    grid-template-columns: 1fr;
  }

  .about__stack-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
