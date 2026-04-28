<template>
  <section class="not-found">
    <div class="container not-found__inner">
      <p class="not-found__code">404</p>
      <h1 class="not-found__title">页面未找到</h1>
      <p class="not-found__desc">你访问的页面不存在或已被移除</p>
      <RouterLink to="/" class="not-found__link">返回首页</RouterLink>
    </div>
  </section>
</template>

<style scoped>
.not-found {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.not-found__inner {
  text-align: center;
  padding: var(--space-3xl) 0;
}

.not-found__code {
  font-size: clamp(4rem, 10vw, 8rem);
  font-weight: 700;
  color: var(--color-border-strong);
  line-height: 1;
  margin: 0;
}

.not-found__title {
  font-size: 1.2rem;
  margin: var(--space-md) 0 var(--space-sm);
  color: var(--color-text-heading);
}

.not-found__desc {
  color: var(--color-text-muted);
  font-size: 0.88rem;
  margin: 0 0 var(--space-xl);
}

.not-found__link {
  display: inline-flex;
  align-items: center;
  padding: 10px 24px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  font-size: 0.85rem;
  transition: all var(--duration-fast) ease;
}

.not-found__link:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}
</style>
