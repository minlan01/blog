<template>
  <div class="admin-page__panel">
    <div v-if="!loaded" class="admin-page__loading">加载中...</div>
    <div v-else class="site-admin">
      <!-- 基础设置 -->
      <div class="site-admin__section">
        <h3 class="site-admin__section-title">基础设置</h3>
        <div class="site-admin__field">
          <label>站点名称</label>
          <input v-model="form.site_name" class="admin-input" placeholder="显示在标题和侧边栏" />
        </div>
        <div class="site-admin__field">
          <label>显示昵称（关于页）</label>
          <input v-model="form.display_name" class="admin-input" placeholder="如：赤夜冥岚" />
        </div>
        <div class="site-admin__field">
          <label>首页公告（侧边栏公告文字）</label>
          <textarea v-model="form.intro_text" class="admin-input admin-input--textarea" placeholder="显示在首页右侧公告区" />
        </div>
        <div class="site-admin__field">
          <label>头像</label>
          <div class="site-admin__avatar-row">
            <img v-if="form.avatar" :src="form.avatar" alt="avatar" class="site-admin__avatar-preview" />
            <input v-model="form.avatar" class="admin-input" placeholder="头像 URL" />
          </div>
        </div>
        <div class="site-admin__field">
          <label>GitHub 链接</label>
          <input v-model="form.github_url" class="admin-input" placeholder="https://github.com/..." />
        </div>
        <div class="site-admin__field">
          <label>联系邮箱</label>
          <input v-model="form.email" class="admin-input" placeholder="your@email.com" />
        </div>
        <div class="site-admin__field">
          <label>位置</label>
          <input v-model="form.location" class="admin-input" placeholder="如：中国云南" />
        </div>
      </div>

      <div class="site-admin__divider"></div>

      <!-- 首页 Opening -->
      <div class="site-admin__section">
        <h3 class="site-admin__section-title">首页 Opening 动画</h3>
        <div class="site-admin__field">
          <label>主标题</label>
          <input v-model="form.hero_title" class="admin-input" />
        </div>
        <div class="site-admin__field">
          <label>副标题</label>
          <input v-model="form.hero_subtitle" class="admin-input" />
        </div>
      </div>

      <div class="site-admin__divider"></div>

      <!-- 关于页内容 -->
      <div class="site-admin__section">
        <h3 class="site-admin__section-title">关于页内容</h3>
        <div class="site-admin__field">
          <label>角色标签</label>
          <input v-model="form.about_role" class="admin-input" placeholder="如：开发者 / 技术记录者" />
        </div>
        <div class="site-admin__field">
          <label>一句话简介</label>
          <textarea v-model="form.about_summary" class="admin-input admin-input--textarea" placeholder="关于页头像旁边的简介" />
        </div>
        <div class="site-admin__field">
          <label>关于我（正文，多段落用空行分隔）</label>
          <textarea v-model="form.about_me" class="admin-input admin-input--textarea admin-input--tall" placeholder="关于页「关于我」区段的正文内容" />
        </div>
        <div class="site-admin__field">
          <label>关于项目（正文，多段落用空行分隔）</label>
          <textarea v-model="form.about_project" class="admin-input admin-input--textarea admin-input--tall" placeholder="关于页「关于项目」区段的正文内容" />
        </div>
        <div class="site-admin__field">
          <label>项目亮点（每行一个，格式：标签|标题|描述）</label>
          <textarea v-model="form.project_highlights" class="admin-input admin-input--textarea admin-input--tall" placeholder="前端|Vue 3 + TypeScript|类型安全的现代化前端框架&#10;后端|FastAPI + SQLAlchemy|高性能 Python API 框架" />
        </div>
        <div class="site-admin__field">
          <label>技术栈（逗号或换行分隔）</label>
          <textarea v-model="form.tech_stack" class="admin-input admin-input--textarea" placeholder="Vue 3, TypeScript, FastAPI, Docker, ..." />
        </div>
      </div>

      <div class="site-admin__divider"></div>

      <!-- ICP 备案 -->
      <div class="site-admin__section">
        <h3 class="site-admin__section-title">ICP 备案（页脚）</h3>
        <div class="site-admin__field">
          <label>备案号</label>
          <input v-model="form.icp_filing" class="admin-input" placeholder="如：滇ICP备2026xxxxxx号" />
        </div>
        <div class="site-admin__field">
          <label>备案链接</label>
          <input v-model="form.icp_link" class="admin-input" placeholder="https://beian.miit.gov.cn/" />
        </div>
      </div>

      <div class="site-admin__actions">
        <button class="site-admin__save" :disabled="saving" @click="handleSave">
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { updateSiteProfile } from '@/api/admin'
import { http } from '@/api/http'
import { useToastStore } from '@/stores/toast'
import type { SiteProfile } from '@/types/blog'

const toast = useToastStore()

const loaded = ref(false)
const saving = ref(false)

const form = reactive({
  site_name: '',
  display_name: '',
  intro_text: '',
  avatar: '',
  github_url: '',
  email: '',
  location: '',
  hero_title: '',
  hero_subtitle: '',
  about_role: '',
  about_summary: '',
  about_me: '',
  about_project: '',
  project_highlights: '',
  tech_stack: '',
  icp_filing: '',
  icp_link: '',
})

async function loadProfile() {
  loaded.value = false
  try {
    const { data } = await http.get<SiteProfile>('/site/profile')
    Object.assign(form, data)
  } catch {
    toast.error('加载站点设置失败')
  } finally {
    loaded.value = true
  }
}

async function handleSave() {
  saving.value = true
  try {
    await updateSiteProfile({ ...form })
    toast.success('站点设置已保存')
  } catch {
    toast.error('保存失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

onMounted(() => loadProfile())
</script>

<style scoped>
.site-admin {
  max-width: 720px;
}

.site-admin__section {
  display: grid;
  gap: var(--space-md);
}

.site-admin__section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin: 0 0 var(--space-xs);
}

.site-admin__field {
  display: grid;
  gap: 4px;
}

.site-admin__field label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.site-admin__field .admin-input {
  width: 100%;
}

.site-admin__divider {
  height: 1px;
  background: var(--color-border);
  margin: var(--space-xl) 0;
}

.site-admin__avatar-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.site-admin__avatar-preview {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--color-border);
  flex-shrink: 0;
}

.site-admin__avatar-row .admin-input {
  flex: 1;
}

.site-admin__actions {
  margin-top: var(--space-xl);
  display: flex;
  justify-content: flex-end;
}

.site-admin__save {
  padding: 10px 32px;
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: var(--color-bg);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.site-admin__save:hover:not(:disabled) {
  opacity: 0.9;
}

.site-admin__save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
