<template>
  <div class="admin-tokens">
    <div class="admin-tokens__header">
      <h3 class="admin-tokens__title">API 令牌管理</h3>
      <button class="admin-tokens__create-btn" @click="showCreate = !showCreate">
        {{ showCreate ? '取消' : '+ 创建令牌' }}
      </button>
    </div>

    <!-- 创建表单 -->
    <div v-if="showCreate" class="admin-tokens__create-form">
      <div class="admin-tokens__field">
        <label class="admin-tokens__label">令牌名称</label>
        <input
          v-model="newTokenName"
          type="text"
          class="admin-tokens__input"
          placeholder="如：AI发文章"
          maxlength="100"
        />
      </div>
      <div class="admin-tokens__field">
        <label class="admin-tokens__label">权限范围</label>
        <input
          v-model="newTokenScopes"
          type="text"
          class="admin-tokens__input"
          placeholder="* (全部权限) 或 posts:create,upload"
        />
        <span class="admin-tokens__hint">可用权限：posts:create（发文章）、upload（上传媒体）、* （全部）</span>
      </div>
      <div class="admin-tokens__field">
        <label class="admin-tokens__label">过期天数（选填）</label>
        <input
          v-model.number="newTokenExpiry"
          type="number"
          class="admin-tokens__input"
          placeholder="不填 = 永不过期"
          min="1"
          max="365"
        />
      </div>
      <button
        class="admin-tokens__confirm-btn"
        :disabled="!newTokenName.trim() || creating"
        @click="handleCreate"
      >
        {{ creating ? '创建中...' : '确认创建' }}
      </button>
    </div>

    <!-- 新创建的令牌（只显示一次） -->
    <div v-if="newlyCreatedToken" class="admin-tokens__new-token">
      <div class="admin-tokens__new-token-warning">
        ⚠️ 令牌只显示这一次，请立即复制保存！关闭后无法再次查看。
      </div>
      <div class="admin-tokens__new-token-value">
        <code>{{ newlyCreatedToken }}</code>
        <button class="admin-tokens__copy-btn" @click="copyToken">复制</button>
      </div>
      <button class="admin-tokens__dismiss-btn" @click="newlyCreatedToken = ''">我已保存</button>
    </div>

    <!-- 加载中 -->
    <div v-if="!loaded" class="admin-page__loading">加载中...</div>

    <!-- 令牌列表 -->
    <div v-else-if="tokens.length === 0" class="admin-tokens__empty">暂无 API 令牌</div>

    <div v-else class="admin-tokens__list">
      <div
        v-for="t in tokens"
        :key="t.id"
        class="admin-tokens__item"
        :class="{ 'admin-tokens__item--revoked': t.revoked }"
      >
        <div class="admin-tokens__item-info">
          <span class="admin-tokens__item-name">{{ t.name }}</span>
          <span class="admin-tokens__item-scope">{{ t.scopes }}</span>
        </div>
        <div class="admin-tokens__item-meta">
          <span class="admin-tokens__item-date">创建于 {{ formatDate(t.created_at) }}</span>
          <span v-if="t.last_used_at" class="admin-tokens__item-used">最后使用 {{ formatDate(t.last_used_at) }}</span>
          <span v-if="t.expires_at" class="admin-tokens__item-expiry">过期 {{ formatDate(t.expires_at) }}</span>
          <span v-if="t.revoked" class="admin-tokens__item-revoked-tag">已撤销</span>
        </div>
        <button
          v-if="!t.revoked"
          class="admin-tokens__revoke-btn"
          @click="handleRevoke(t.id, t.name)"
        >
          撤销
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getTokens, createToken, revokeToken, type ApiToken } from '@/api/admin'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const tokens = ref<ApiToken[]>([])
const loaded = ref(false)

const showCreate = ref(false)
const newTokenName = ref('')
const newTokenScopes = ref('*')
const newTokenExpiry = ref<number | undefined>(undefined)
const creating = ref(false)
const newlyCreatedToken = ref('')

async function loadTokens() {
  try {
    tokens.value = await getTokens()
  } catch {
    toast.error('加载令牌失败')
  } finally {
    loaded.value = true
  }
}

async function handleCreate() {
  creating.value = true
  try {
    const res = await createToken({
      name: newTokenName.value.trim(),
      scopes: newTokenScopes.value.trim() || '*',
      expires_in_days: newTokenExpiry.value || undefined,
    })
    newlyCreatedToken.value = res.token
    tokens.value.unshift(res.token_info)
    newTokenName.value = ''
    newTokenScopes.value = '*'
    newTokenExpiry.value = undefined
    showCreate.value = false
    toast.success('令牌创建成功')
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

async function handleRevoke(id: number, name: string) {
  if (!confirm(`确定撤销令牌「${name}」？此操作不可逆，撤销后立即失效。`)) return
  try {
    await revokeToken(id)
    const t = tokens.value.find(x => x.id === id)
    if (t) t.revoked = true
    toast.success('令牌已撤销')
  } catch {
    toast.error('撤销失败')
  }
}

function copyToken() {
  navigator.clipboard.writeText(newlyCreatedToken.value).then(() => {
    toast.success('已复制到剪贴板')
  }).catch(() => {
    toast.error('复制失败，请手动复制')
  })
}

function formatDate(iso: string): string {
  const d = new Date(iso)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(loadTokens)
</script>

<style scoped>
.admin-tokens__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.admin-tokens__title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text-heading);
}

.admin-tokens__create-btn {
  padding: 0.4rem 1rem;
  background: var(--color-accent);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.8rem;
  transition: opacity 0.15s;
}

.admin-tokens__create-btn:hover {
  opacity: 0.9;
}

.admin-tokens__create-form {
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  background: var(--glass-card-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
}

.admin-tokens__field {
  margin-bottom: 1rem;
}

.admin-tokens__label {
  display: block;
  font-size: 0.8rem;
  color: var(--color-text-muted);
  margin-bottom: 0.35rem;
}

.admin-tokens__input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: var(--glass-surface-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  font-size: 0.85rem;
}

.admin-tokens__input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.admin-tokens__hint {
  display: block;
  font-size: 0.7rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}

.admin-tokens__confirm-btn {
  padding: 0.5rem 1.5rem;
  background: var(--color-accent);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.85rem;
}

.admin-tokens__confirm-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.admin-tokens__new-token {
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid var(--color-ochre);
  border-radius: var(--radius-lg);
}

.admin-tokens__new-token-warning {
  font-size: 0.8rem;
  color: var(--color-ochre);
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.admin-tokens__new-token-value {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.75rem;
}

.admin-tokens__new-token-value code {
  flex: 1;
  padding: 0.5rem 0.75rem;
  background: var(--color-bg-soft);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  word-break: break-all;
  color: var(--color-text);
}

.admin-tokens__copy-btn {
  padding: 0.4rem 0.75rem;
  background: var(--glass-surface-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  cursor: pointer;
  font-size: 0.75rem;
  white-space: nowrap;
}

.admin-tokens__dismiss-btn {
  padding: 0.35rem 1rem;
  background: transparent;
  color: var(--color-text-muted);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.75rem;
}

.admin-tokens__empty {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.admin-tokens__list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.admin-tokens__item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.85rem 1rem;
  background: var(--glass-card-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  transition: border-color 0.15s;
}

.admin-tokens__item--revoked {
  opacity: 0.5;
}

.admin-tokens__item-info {
  flex: 1;
  min-width: 0;
}

.admin-tokens__item-name {
  display: block;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text-heading);
}

.admin-tokens__item-scope {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.admin-tokens__item-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.7rem;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.admin-tokens__item-revoked-tag {
  color: var(--color-ochre);
  font-weight: 600;
}

.admin-tokens__revoke-btn {
  padding: 0.3rem 0.75rem;
  background: transparent;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  color: var(--color-ochre);
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.15s;
  flex-shrink: 0;
}

.admin-tokens__revoke-btn:hover {
  background: rgba(245, 158, 11, 0.1);
  border-color: var(--color-ochre);
}

@media (max-width: 768px) {
  .admin-tokens__item {
    flex-wrap: wrap;
  }
  .admin-tokens__item-meta {
    flex-basis: 100%;
    flex-wrap: wrap;
  }
}
</style>
