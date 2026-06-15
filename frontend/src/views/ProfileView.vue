<template>
  <section class="profile">
    <div class="container narrow-container">
      <header class="profile__header">
        <span class="profile__label">个人资料</span>
        <h1 class="profile__title">{{ authStore.user?.username || '个人中心' }}</h1>
      </header>

      <div class="profile__card" v-if="authStore.user">
        <div class="profile__info">
          <div class="profile__field">
            <span class="profile__field-label">用户名</span>
            <span class="profile__value">{{ authStore.user.username }}</span>
          </div>
          <div class="profile__field" v-if="authStore.user.email">
            <span class="profile__field-label">邮箱</span>
            <span class="profile__value">{{ authStore.user.email }}</span>
          </div>
          <div class="profile__field">
            <span class="profile__field-label">角色</span>
            <span class="profile__value">
              <span class="profile__role" :class="{ 'profile__role--admin': authStore.isAdmin }">
                {{ authStore.isAdmin ? '管理员' : '用户' }}
              </span>
            </span>
          </div>
          <div class="profile__field">
            <span class="profile__field-label">注册时间</span>
            <span class="profile__value">{{ formatDate((authStore.user as any).created_at) }}</span>
          </div>
        </div>

        <div class="profile__actions">
          <button class="profile__logout" @click="handleLogout">退出登录</button>
        </div>
      </div>

      <div v-else class="profile__empty">
        <p>请先登录查看个人资料</p>
        <RouterLink to="/login" class="profile__login-link">登录</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric'
  })
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.profile {
  padding: var(--space-3xl) 0;
}

/* 移除全局毛玻璃（profile__card 自带玻璃效果） */
.profile > .container {
  background: none;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  border: none;
  padding: 0;
  border-radius: 0;
}

.profile__header {
  margin-bottom: var(--space-2xl);
}

.profile__label {
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.profile__title {
  font-size: clamp(1.5rem, 3vw, 2rem);
  margin: var(--space-xs) 0 0;
}

.profile__card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  padding: var(--space-2xl);
  box-shadow: var(--shadow-card);
}

.profile__info {
  display: grid;
  gap: var(--space-md);
  margin-bottom: var(--space-xl);
}

.profile__field {
  display: flex;
  align-items: baseline;
  gap: var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--color-border);
}

.profile__field-label {
  min-width: 90px;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.profile__value {
  font-size: 0.9rem;
  color: var(--color-text);
}

.profile__role {
  font-size: 0.78rem;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  background: var(--color-surface-hover);
  color: var(--color-text-muted);
}

.profile__role--admin {
  background: var(--accent-tint-10);
  color: var(--color-accent);
}

.profile__actions {
  padding-top: var(--space-md);
}

.profile__logout {
  padding: 8px 20px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  font-size: 0.82rem;
  background: transparent;
  transition: all var(--duration-fast) ease;
}

.profile__logout:hover {
  border-color: var(--color-ochre);
  color: var(--color-ochre);
}

.profile__empty {
  text-align: center;
  padding: var(--space-2xl);
  color: var(--color-text-muted);
  font-size: 0.88rem;
}

.profile__login-link {
  display: inline-block;
  margin-top: var(--space-md);
  color: var(--color-accent);
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .profile {
    padding: var(--space-xl) 0;
  }

  .profile__card {
    padding: var(--space-xl);
  }

  .profile__field {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-xs);
  }

  .profile__field-label {
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .profile__card {
    padding: var(--space-lg);
  }

  .profile__field {
    padding-bottom: var(--space-sm);
  }

  .profile__actions {
    padding-top: var(--space-sm);
  }
}
</style>
