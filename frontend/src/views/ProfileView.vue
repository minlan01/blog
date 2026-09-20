<template>
  <section class="profile">
    <div class="container narrow-container">
      <header class="profile__header">
        <span class="profile__label">个人资料</span>
        <h1 class="profile__title">{{ authStore.user?.username || '个人中心' }}</h1>
      </header>

      <div v-if="authStore.user" class="profile__card">
        <!-- 基本信息展示 -->
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

        <!-- 编辑区 Tabs -->
        <div class="profile__tabs">
          <button
            class="profile__tab"
            :class="{ 'profile__tab--active': activeTab === 'edit' }"
            @click="activeTab = 'edit'"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            编辑资料
          </button>
          <button
            class="profile__tab"
            :class="{ 'profile__tab--active': activeTab === 'password' }"
            @click="activeTab = 'password'"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            修改密码
          </button>
          <button
            class="profile__tab"
            :class="{ 'profile__tab--active': activeTab === 'bookmarks' }"
            @click="activeTab = 'bookmarks'"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
            我的收藏
          </button>
        </div>

        <!-- 编辑资料面板 -->
        <div v-if="activeTab === 'edit'" class="profile__panel">
          <form class="profile__form" @submit.prevent="handleSaveProfile">
            <div class="profile__avatar-editor">
              <img
                v-if="profileForm.avatar"
                :src="profileForm.avatar"
                alt="头像预览"
                class="profile__avatar-preview"
              />
              <div v-else class="profile__avatar-placeholder">
                {{ authStore.user.username.charAt(0).toUpperCase() }}
              </div>
              <div class="profile__avatar-actions">
                <label class="profile__upload-btn">
                  上传头像
                  <input
                    type="file"
                    accept="image/*"
                    @change="handleAvatarUpload"
                    hidden
                  />
                </label>
                <button
                  v-if="profileForm.avatar"
                  type="button"
                  class="profile__clear-avatar"
                  @click="profileForm.avatar = ''"
                >移除</button>
                <span class="profile__avatar-hint">或直接粘贴图片链接到下方</span>
              </div>
            </div>

            <div class="profile__form-field">
              <label class="profile__form-label">头像链接</label>
              <input
                v-model="profileForm.avatar"
                type="url"
                class="profile__form-input"
                placeholder="https://..."
                maxlength="500"
              />
            </div>
            <div class="profile__form-field">
              <label class="profile__form-label">个性签名</label>
              <textarea
                v-model="profileForm.bio"
                class="profile__form-input profile__form-textarea"
                placeholder="一句话介绍自己"
                maxlength="200"
              ></textarea>
            </div>
            <div class="profile__form-field">
              <label class="profile__form-label">邮箱</label>
              <input
                v-model="profileForm.email"
                type="email"
                class="profile__form-input"
                placeholder="you@example.com"
              />
            </div>
            <div class="profile__form-actions">
              <button type="submit" class="profile__save-btn" :disabled="profileSaving">
                {{ profileSaving ? '保存中...' : '保存资料' }}
              </button>
            </div>
          </form>
        </div>

        <!-- 修改密码面板 -->
        <div v-if="activeTab === 'password'" class="profile__panel">
          <form class="profile__form" @submit.prevent="handleChangePassword">
            <div class="profile__form-field">
              <label class="profile__form-label">当前密码</label>
              <input
                v-model="passwordForm.oldPassword"
                type="password"
                class="profile__form-input"
                placeholder="输入当前密码"
                required
                autocomplete="current-password"
              />
            </div>
            <div class="profile__form-field">
              <label class="profile__form-label">新密码</label>
              <input
                v-model="passwordForm.newPassword"
                type="password"
                class="profile__form-input"
                placeholder="至少 8 位，含大小写字母和数字"
                required
                minlength="8"
                autocomplete="new-password"
              />
            </div>
            <div class="profile__form-field">
              <label class="profile__form-label">确认新密码</label>
              <input
                v-model="passwordForm.confirmPassword"
                type="password"
                class="profile__form-input"
                placeholder="再次输入新密码"
                required
                autocomplete="new-password"
              />
            </div>
            <p v-if="passwordError" class="profile__form-error">{{ passwordError }}</p>
            <div class="profile__form-actions">
              <button type="submit" class="profile__save-btn" :disabled="passwordSaving">
                {{ passwordSaving ? '修改中...' : '修改密码' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Bookmarks panel -->
        <div v-if="activeTab === 'bookmarks'" class="profile__panel">
          <div v-if="bookmarkLoading" class="profile__panel-loading">加载中...</div>
          <div v-else-if="bookmarks.length === 0" class="profile__panel-empty">
            还没有收藏任何文章。去
            <RouterLink to="/posts" class="profile__link">浏览文章</RouterLink>
            收藏你喜欢的吧。
          </div>
          <div v-else class="profile__bookmarks">
            <RouterLink
              v-for="post in bookmarks"
              :key="post.id"
              :to="`/posts/${post.slug}`"
              class="profile__bookmark-card"
            >
              <h4 class="profile__bookmark-title">{{ post.title }}</h4>
              <p class="profile__bookmark-summary" v-if="post.summary">{{ post.summary }}</p>
              <span class="profile__bookmark-meta">{{ formatDate(post.published_at) }}</span>
            </RouterLink>
          </div>
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
import { reactive, ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { changePassword, updateMyProfile, uploadAvatar } from '@/api/auth'
import { getMyBookmarks } from '@/api/reactions'
import { useToastStore } from '@/stores/toast'
import type { PostSummary } from '@/types/blog'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToastStore()

const activeTab = ref<'edit' | 'password' | 'bookmarks'>('edit')
const bookmarks = ref<PostSummary[]>([])
const bookmarkLoading = ref(true)

const profileForm = reactive({
  avatar: authStore.user?.avatar ?? '',
  bio: authStore.user?.bio ?? '',
  email: authStore.user?.email ?? '',
})
const profileSaving = ref(false)

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})
const passwordSaving = ref(false)
const passwordError = ref('')

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric'
  })
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}

async function handleAvatarUpload(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  try {
    toast.info('上传中...')
    const result = await uploadAvatar(file)
    profileForm.avatar = result.avatar
    toast.success('头像上传成功')
  } catch {
    toast.error('头像上传失败，请稍后重试')
  } finally {
    target.value = ''
  }
}

async function handleSaveProfile() {
  profileSaving.value = true
  try {
    const updated = await updateMyProfile({
      avatar: profileForm.avatar || undefined,
      bio: profileForm.bio || undefined,
      email: profileForm.email || undefined,
    })
    authStore.setUser(updated)
    toast.success('资料保存成功')
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    toast.error(typeof detail === 'string' ? detail : '保存失败，请稍后重试')
  } finally {
    profileSaving.value = false
  }
}

async function handleChangePassword() {
  passwordError.value = ''
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }
  if (passwordForm.newPassword.length < 8) {
    passwordError.value = '新密码至少 8 位'
    return
  }
  passwordSaving.value = true
  try {
    await changePassword(passwordForm.oldPassword, passwordForm.newPassword)
    toast.success('密码修改成功，请重新登录')
    authStore.logout()
    router.push('/login')
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    if (Array.isArray(detail)) {
      passwordError.value = detail.map((d: any) => d.msg || String(d)).join('；')
    } else {
      passwordError.value = typeof detail === 'string' ? detail : '密码修改失败，请检查旧密码是否正确'
    }
  } finally {
    passwordSaving.value = false
  }
}

async function loadBookmarks() {
  bookmarkLoading.value = true
  try {
    bookmarks.value = await getMyBookmarks()
  } catch {
    bookmarks.value = []
  } finally {
    bookmarkLoading.value = false
  }
}

onMounted(() => {
  if (authStore.isLoggedIn) {
    loadBookmarks()
  }
})

watch(() => authStore.isLoggedIn, (loggedIn) => {
  if (loggedIn) {
    loadBookmarks()
    profileForm.avatar = authStore.user?.avatar ?? ''
    profileForm.bio = authStore.user?.bio ?? ''
    profileForm.email = authStore.user?.email ?? ''
  }
})
</script>

<style scoped>
.profile {
  padding: var(--space-3xl) 0;
}

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
  cursor: pointer;
}

.profile__logout:hover {
  border-color: var(--color-ochre);
  color: var(--color-ochre);
}

/* Tabs */
.profile__tabs {
  display: flex;
  gap: var(--space-sm);
  margin-top: var(--space-xl);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border);
  flex-wrap: wrap;
}

.profile__tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: none;
  color: var(--color-text-muted);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.profile__tab:hover {
  color: var(--color-text);
  border-color: var(--border-heavy);
}

.profile__tab--active {
  color: var(--color-accent);
  border-color: var(--color-accent);
  background: var(--accent-tint-08);
}

/* Panel */
.profile__panel {
  margin-top: var(--space-lg);
}

.profile__panel-loading,
.profile__panel-empty {
  padding: var(--space-xl);
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.88rem;
}

.profile__link {
  color: var(--color-accent);
  font-weight: 500;
}

/* Form */
.profile__form {
  display: grid;
  gap: var(--space-md);
  max-width: 520px;
}

.profile__avatar-editor {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--color-border);
}

.profile__avatar-preview {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-border);
}

.profile__avatar-placeholder {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 600;
  background: var(--accent-tint-10);
  color: var(--color-accent);
}

.profile__avatar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.profile__upload-btn {
  display: inline-block;
  padding: 6px 14px;
  border: 1px solid var(--accent-tint-30);
  border-radius: var(--radius-sm);
  background: var(--accent-tint-06);
  color: var(--color-accent);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.profile__upload-btn:hover {
  background: var(--accent-tint-15);
  border-color: var(--color-accent);
}

.profile__clear-avatar {
  padding: 6px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: none;
  color: var(--color-text-muted);
  font-size: 0.82rem;
  cursor: pointer;
}

.profile__clear-avatar:hover {
  color: #f87171;
  border-color: var(--error-border-30, rgba(248, 113, 113, 0.3));
}

.profile__avatar-hint {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  opacity: 0.7;
}

.profile__form-field {
  display: grid;
  gap: 6px;
}

.profile__form-label {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.profile__form-input {
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: border-color var(--duration-fast) ease;
}

.profile__form-input::placeholder {
  color: var(--color-text-muted);
  opacity: 0.6;
}

.profile__form-input:focus {
  border-color: var(--color-accent);
}

.profile__form-textarea {
  resize: vertical;
  min-height: 72px;
}

.profile__form-error {
  margin: 0;
  padding: 8px 12px;
  font-size: 0.82rem;
  color: #f87171;
  background: rgba(248, 113, 113, 0.08);
  border: 1px solid rgba(248, 113, 113, 0.2);
  border-radius: var(--radius-sm);
}

.profile__form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: var(--space-xs);
}

.profile__save-btn {
  padding: 10px 28px;
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: var(--color-bg);
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.profile__save-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.profile__save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.profile__bookmarks {
  display: grid;
  gap: var(--space-md);
}

.profile__bookmark-card {
  display: block;
  padding: var(--space-md) var(--space-lg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  text-decoration: none;
  transition: all var(--duration-fast) ease;
}

.profile__bookmark-card:hover {
  border-color: var(--color-accent);
  transform: translateX(4px);
}

.profile__bookmark-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin: 0 0 var(--space-xs);
}

.profile__bookmark-summary {
  font-size: 0.82rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin: 0 0 var(--space-xs);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.profile__bookmark-meta {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  opacity: 0.7;
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

@media (max-width: 768px) {
  .profile { padding: var(--space-xl) 0; }
  .profile__card { padding: var(--space-xl); }
  .profile__field { flex-direction: column; align-items: flex-start; gap: var(--space-xs); }
  .profile__field-label { min-width: auto; }
}

@media (max-width: 480px) {
  .profile__card { padding: var(--space-lg); }
  .profile__field { padding-bottom: var(--space-sm); }
  .profile__actions { padding-top: var(--space-sm); }
  .profile__avatar-editor { flex-direction: column; align-items: flex-start; }
}
</style>
