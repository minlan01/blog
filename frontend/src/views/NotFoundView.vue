<template>
  <section class="not-found">
    <div class="container not-found__inner">
      <div class="not-found__glitch">
        <span class="not-found__code" data-text="404">404</span>
      </div>
      <h1 class="not-found__title">SIGNAL LOST</h1>
      <p class="not-found__desc">页面信号丢失或已被移除</p>
      <div class="not-found__scanlines"></div>
      <RouterLink to="/" class="not-found__link">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        返回首页
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.not-found {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.not-found__inner {
  text-align: center;
  padding: var(--space-3xl) 0;
  position: relative;
}

/* ── Glitch 404 ── */
.not-found__glitch {
  position: relative;
  display: inline-block;
  margin-bottom: var(--space-md);
}

.not-found__code {
  font-family: var(--font-display, 'Inter', monospace);
  font-size: clamp(5rem, 14vw, 10rem);
  font-weight: 800;
  line-height: 1;
  color: var(--color-text-heading);
  position: relative;
  letter-spacing: -0.03em;
}

.not-found__code::before,
.not-found__code::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* Red channel glitch */
.not-found__code::before {
  color: #ff0040;
  animation: glitch-red 2.5s infinite linear alternate-reverse;
  clip-path: polygon(0 0, 100% 0, 100% 33%, 0 33%);
}

/* Cyan channel glitch */
.not-found__code::after {
  color: #00fff0;
  animation: glitch-cyan 2s infinite linear alternate-reverse;
  clip-path: polygon(0 67%, 100% 67%, 100% 100%, 0 100%);
}

@keyframes glitch-red {
  0%   { transform: translate(0); }
  10%  { transform: translate(-2px, 1px); }
  20%  { transform: translate(2px, -1px); }
  30%  { transform: translate(-1px, 2px); clip-path: polygon(0 10%, 100% 10%, 100% 35%, 0 35%); }
  40%  { transform: translate(1px, -2px); }
  50%  { transform: translate(-3px, 0); clip-path: polygon(0 5%, 100% 5%, 100% 40%, 0 40%); }
  60%  { transform: translate(3px, 1px); }
  70%  { transform: translate(-1px, -1px); clip-path: polygon(0 15%, 100% 15%, 100% 45%, 0 45%); }
  80%  { transform: translate(2px, 2px); }
  90%  { transform: translate(-2px, -1px); }
  100% { transform: translate(0); }
}

@keyframes glitch-cyan {
  0%   { transform: translate(0); }
  15%  { transform: translate(2px, -1px); clip-path: polygon(0 60%, 100% 60%, 100% 85%, 0 85%); }
  30%  { transform: translate(-2px, 1px); }
  45%  { transform: translate(1px, 2px); clip-path: polygon(0 70%, 100% 70%, 100% 95%, 0 95%); }
  60%  { transform: translate(-1px, -2px); }
  75%  { transform: translate(3px, 0); clip-path: polygon(0 55%, 100% 55%, 100% 80%, 0 80%); }
  90%  { transform: translate(-3px, 1px); }
  100% { transform: translate(0); }
}

/* ── Title ── */
.not-found__title {
  font-family: var(--font-display, 'Inter', monospace);
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 0.3em;
  color: var(--color-text-muted);
  margin: var(--space-md) 0 var(--space-xs);
  text-transform: uppercase;
}

.not-found__desc {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin: 0 0 var(--space-xl);
  opacity: 0.7;
}

/* ── Scanlines overlay ── */
.not-found__scanlines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    transparent 0,
    transparent 2px,
    rgba(0, 0, 0, 0.03) 2px,
    rgba(0, 0, 0, 0.03) 4px
  );
  animation: scanline-move 8s linear infinite;
  opacity: 0.6;
}

@keyframes scanline-move {
  0%   { background-position: 0 0; }
  100% { background-position: 0 100px; }
}

/* ── Link ── */
.not-found__link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 24px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  font-size: 0.85rem;
  text-decoration: none;
  transition: all var(--duration-fast) ease;
}

.not-found__link:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  box-shadow: 0 0 20px rgba(129, 140, 248, 0.15);
}

.not-found__link svg {
  transition: transform var(--duration-fast) ease;
}

.not-found__link:hover svg {
  transform: translateX(-3px);
}

@media (prefers-reduced-motion: reduce) {
  .not-found__code::before,
  .not-found__code::after,
  .not-found__scanlines {
    animation: none !important;
  }
}
</style>
