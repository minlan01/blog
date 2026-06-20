<template>
  <section class="about">
    <div class="container narrow-container">
      <header class="about__hero">
        <div class="about__hero-content">
          <div class="about__avatar-wrap">
            <img src="/images/about-avatar.png" alt="赤夜冥岚头像" class="about__avatar" />
            <span class="about__status">MINLAN01</span>
          </div>

          <div class="about__intro">
            <span class="about__kicker">ABOUT</span>
            <h1>赤夜冥岚</h1>
            <p class="about__role">开发者 / 技术记录者 / 个人博客维护者</p>
            <p class="about__summary">
              这里是我沉淀学习、整理项目经验和记录想法的地方。比起把知识停留在脑子里，我更喜欢把一次次实践、踩坑和复盘写下来，让它们变成以后还能被自己和别人重新使用的内容。
            </p>
          </div>
        </div>
      </header>

      <section class="about__section">
        <div class="about__section-label">
          <span>01</span>
          <h2>关于我</h2>
        </div>
        <div class="about__text">
          <p>
            你好，我是赤夜冥岚，也可以叫我 minlan01。来自中国云南，平时主要关注编程、Web 开发、自动化工具和各种能把想法做成真实作品的技术。
          </p>
          <p>
            这个博客不只是一个文章展示页，它更像我的个人工作台：记录学习过程，整理解决问题的方法，也保存一些项目从零到可用之间的真实痕迹。
          </p>
          <p>
            我希望这里的内容保持直接、可复用、能落地。哪怕只是一个很小的问题，只要它被认真写下来，下次遇到时就会少走一点弯路。
          </p>
        </div>
      </section>

      <div class="about__divider"></div>

      <section class="about__section">
        <div class="about__section-label">
          <span>02</span>
          <h2>联系方式</h2>
        </div>
        <div class="about__contact-grid">
          <a class="about__contact-item" href="mailto:746408662@qq.com">
            <span class="about__contact-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <path d="m22 6-10 7L2 6" />
              </svg>
            </span>
            <span>
              <strong>EMAIL</strong>
              <em>746408662@qq.com</em>
            </span>
          </a>

          <a class="about__contact-item" href="https://github.com/minlan01" target="_blank" rel="noopener">
            <span class="about__contact-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                <path d="M12 .5A11.5 11.5 0 0 0 8.36 22.9c.58.1.79-.25.79-.56v-2.02c-3.2.7-3.88-1.38-3.88-1.38-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.78 1.2 1.78 1.2 1.04 1.77 2.72 1.26 3.38.96.11-.75.41-1.26.74-1.55-2.56-.29-5.25-1.28-5.25-5.7 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18A10.9 10.9 0 0 1 12 6.1c.96 0 1.93.13 2.83.38 2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.43-2.7 5.41-5.27 5.7.42.36.79 1.07.79 2.16v3.03c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5Z" />
              </svg>
            </span>
            <span>
              <strong>GITHUB</strong>
              <em>github.com/minlan01</em>
            </span>
          </a>

          <div class="about__contact-item">
            <span class="about__contact-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 10c0 5.5-8 11-8 11S4 15.5 4 10a8 8 0 1 1 16 0Z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
            </span>
            <span>
              <strong>LOCATION</strong>
              <em>中国云南</em>
            </span>
          </div>
        </div>
      </section>

      <div class="about__divider"></div>

      <section class="about__section">
        <div class="about__section-label">
          <span>03</span>
          <h2>关于项目</h2>
        </div>
        <div class="about__text">
          <p>
            这是一个前后端分离的个人博客系统。前台负责阅读、归档、搜索、留言和 AI 对话体验，后台负责文章、分类、标签、媒体库、评论与站点资料管理。
          </p>
          <p>
            前端使用 Vue 3、TypeScript、Vite、Pinia 和 Vue Router 构建；后端使用 FastAPI、SQLAlchemy 与 Pydantic 提供 API、认证和数据管理。项目通过 Docker Compose 编排，前端由 Nginx 提供静态服务，后端和上传目录独立持久化。
          </p>
          <p>
            当前 AI 功能已经切换为 DeepSeek API 接入，不再依赖本机 llama.cpp。数据库默认使用 SQLite，适合个人博客这类轻量场景；后续如果访问量明显增加，也可以迁移到 MySQL 或 PostgreSQL。
          </p>
        </div>

        <div class="about__feature-grid">
          <article v-for="item in projectHighlights" :key="item.title" class="about__feature">
            <span>{{ item.tag }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.text }}</p>
          </article>
        </div>
      </section>

      <div class="about__divider"></div>

      <section class="about__section">
        <div class="about__section-label">
          <span>04</span>
          <h2>技术栈</h2>
        </div>
        <div class="about__stack-grid">
          <div v-for="item in techStack" :key="item" class="about__stack-item">
            {{ item }}
          </div>
        </div>
      </section>

      <footer class="about__footer">
        <span>// Thanks for visiting.</span>
      </footer>
    </div>
  </section>
</template>

<script setup lang="ts">
const projectHighlights = [
  {
    tag: 'Writing',
    title: '文章与归档',
    text: '支持 Markdown 写作、分类标签、搜索和归档，适合长期沉淀技术内容。',
  },
  {
    tag: 'Admin',
    title: '后台管理',
    text: '提供文章编辑、媒体库、评论、留言和站点资料管理，日常维护可以直接在网页里完成。',
  },
  {
    tag: 'AI',
    title: 'DeepSeek 对话',
    text: 'AI 助手通过 DeepSeek API 提供服务，部署时只需要配置对应密钥即可使用。',
  },
]

const techStack = [
  'Vue 3',
  'TypeScript',
  'Vite',
  'Pinia',
  'Vue Router',
  'Axios',
  'FastAPI',
  'SQLAlchemy',
  'SQLite',
  'Docker',
  'Nginx',
  'DeepSeek API',
]
</script>

<style scoped>
.about {
  padding: var(--space-3xl) 0;
}

.about__hero,
.about__section {
  position: relative;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  background: var(--glass-bg-strong);
  box-shadow: var(--glass-card-shadow);
  backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-card-saturate));
}

.about__hero {
  padding: clamp(24px, 5vw, 44px);
  margin-bottom: var(--space-2xl);
  overflow: hidden;
}

.about__hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(135deg, var(--accent-tint-12), transparent 44%),
    linear-gradient(90deg, transparent, var(--accent-tint-08));
  pointer-events: none;
}

.about__hero-content {
  position: relative;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: clamp(22px, 4vw, 36px);
  align-items: center;
}

.about__avatar-wrap {
  position: relative;
  width: clamp(116px, 20vw, 160px);
}

.about__avatar {
  display: block;
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border: 2px solid var(--border-strong);
  border-radius: var(--radius-xl);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.36);
}

.about__status {
  position: absolute;
  right: -8px;
  bottom: -8px;
  padding: 5px 10px;
  border: 1px solid rgba(52, 211, 153, 0.35);
  border-radius: var(--radius-full);
  background: rgba(12, 20, 28, 0.88);
  color: #34d399;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.about__intro {
  min-width: 0;
}

.about__kicker {
  display: inline-flex;
  margin-bottom: 8px;
  color: var(--color-accent);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
}

.about__intro h1 {
  margin: 0;
  color: var(--color-text-heading);
  font-size: clamp(2.2rem, 5vw, 3.2rem);
  font-weight: 750;
  line-height: 1.08;
}

.about__role {
  margin: 10px 0 0;
  color: var(--color-accent);
  font-family: var(--font-mono);
  font-size: 0.88rem;
}

.about__summary {
  max-width: 680px;
  margin: 18px 0 0;
  color: var(--color-text-soft);
  font-size: 0.96rem;
  line-height: 1.9;
}

.about__section {
  padding: clamp(22px, 4vw, 32px);
  margin-bottom: var(--space-2xl);
}

.about__section-label {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.about__section-label span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 34px;
  height: 24px;
  border: 1px solid var(--accent-tint-20);
  border-radius: var(--radius-sm);
  background: var(--accent-tint-06);
  color: var(--color-accent);
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
}

.about__section-label h2 {
  margin: 0;
  color: var(--color-text-heading);
  font-size: 1.2rem;
  font-weight: 650;
}

.about__text {
  display: grid;
  gap: var(--space-md);
}

.about__text p {
  margin: 0;
  color: var(--color-text-soft);
  font-size: 0.94rem;
  line-height: 1.9;
}

.about__divider {
  height: 1px;
  margin: calc(var(--space-2xl) * -0.5) 0 var(--space-2xl);
  background: linear-gradient(90deg, transparent, var(--border-default) 20%, var(--border-default) 80%, transparent);
}

.about__contact-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-md);
}

.about__contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  padding: 14px 16px;
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  background: var(--glass-surface-bg);
  color: inherit;
  text-decoration: none;
  transition: transform var(--duration-fast) ease, border-color var(--duration-fast) ease, background var(--duration-fast) ease;
}

.about__contact-item:hover {
  border-color: var(--accent-tint-30);
  background: var(--accent-tint-04);
  transform: translateY(-1px);
}

.about__contact-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  background: var(--accent-tint-08);
  color: var(--color-accent);
}

.about__contact-item span:last-child {
  min-width: 0;
}

.about__contact-item strong,
.about__contact-item em {
  display: block;
  font-style: normal;
}

.about__contact-item strong {
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  font-size: 0.64rem;
  letter-spacing: 0.12em;
}

.about__contact-item em {
  margin-top: 3px;
  color: var(--color-text-soft);
  font-size: 0.84rem;
  overflow-wrap: anywhere;
}

.about__feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-md);
  margin-top: var(--space-xl);
}

.about__feature {
  padding: 18px;
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  background: var(--glass-surface-bg);
}

.about__feature span {
  color: var(--color-accent);
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.about__feature h3 {
  margin: 9px 0 8px;
  color: var(--color-text-heading);
  font-size: 1rem;
}

.about__feature p {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.84rem;
  line-height: 1.7;
}

.about__stack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.about__stack-item {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 10px 12px;
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  background: var(--glass-surface-bg);
  color: var(--color-text-soft);
  font-size: 0.84rem;
  font-weight: 650;
  text-align: center;
}

.about__footer {
  padding: var(--space-lg) 0;
  text-align: center;
}

.about__footer span {
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  font-size: 0.78rem;
  opacity: 0.6;
}

@media (max-width: 760px) {
  .about__hero-content {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
  }

  .about__contact-grid,
  .about__feature-grid {
    grid-template-columns: 1fr;
  }

  .about__summary {
    font-size: 0.92rem;
  }
}

@media (max-width: 520px) {
  .about__stack-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
