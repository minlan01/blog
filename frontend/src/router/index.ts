import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: DefaultLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/HomeView.vue'),
          meta: { title: '首页', description: 'minlan01 的技术博客 — 分享编程技术、项目经验与开发心得' },
        },
        {
          path: 'posts',
          name: 'posts',
          component: () => import('@/views/PostsView.vue'),
          meta: { title: '文章', description: '浏览所有技术文章，涵盖前后端开发、系统设计等领域' },
        },
        {
          path: 'posts/:slug',
          name: 'post-detail',
          component: () => import('@/views/PostDetailView.vue'),
          meta: { title: '文章详情' },
        },
        {
          path: 'about',
          name: 'about',
          component: () => import('@/views/AboutView.vue'),
          meta: { title: '关于', description: '了解 minlan01 — 一个热爱技术的开发者' },
        },
        {
          path: 'login',
          name: 'login',
          component: () => import('@/views/LoginView.vue'),
          meta: { title: '登录', description: '登录 minlan01 博客账号' },
        },
        {
          path: 'register',
          name: 'register',
          component: () => import('@/views/RegisterView.vue'),
          meta: { title: '注册', description: '注册 minlan01 博客账号' },
        },
        {
          path: 'forgot-password',
          name: 'forgot-password',
          component: () => import('@/views/ForgotPasswordView.vue'),
          meta: { title: '忘记密码', description: '重置你的博客密码' },
        },
        {
          path: 'reset-password',
          name: 'reset-password',
          component: () => import('@/views/ResetPasswordView.vue'),
          meta: { title: '重置密码', description: '设置新密码' },
        },
        {
          path: 'verify-email',
          name: 'verify-email',
          component: () => import('@/views/VerifyEmailView.vue'),
          meta: { title: '验证邮箱', description: '验证你的邮箱地址' },
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue'),
          meta: { title: '个人资料', requiresAuth: true, description: '管理你的个人资料' },
        },
        {
          path: 'admin',
          name: 'admin',
          component: () => import('@/views/AdminView.vue'),
          meta: { title: '后台管理', requiresAuth: true, requiresAdmin: true, description: '博客后台管理面板' },
        },
        {
          path: 'create-post',
          name: 'create-post',
          component: () => import('@/views/CreatePostView.vue'),
          meta: { title: '写文章', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'edit-post/:id',
          name: 'edit-post',
          component: () => import('@/views/EditPostView.vue'),
          meta: { title: '编辑文章', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'search',
          name: 'search',
          component: () => import('@/views/SearchResultsView.vue'),
          meta: { title: '搜索', description: '搜索博客文章' },
        },
        {
          path: 'category/:slug',
          name: 'category-posts',
          component: () => import('@/views/CategoryPostsView.vue'),
          meta: { title: '分类文章' },
        },
        {
          path: 'archive',
          name: 'archive',
          component: () => import('@/views/ArchiveView.vue'),
          meta: { title: '归档', description: '按时间归档浏览所有文章' },
        },
        {
          path: 'link',
          name: 'friend-links',
          component: () => import('@/views/FriendLinksView.vue'),
          meta: { title: '友链', description: '友情链接 — 与优秀的技术博客互链' },
        },
        {
          path: 'message-board',
          name: 'message-board',
          component: () => import('@/views/MessageBoardView.vue'),
          meta: { title: '留言板', description: '欢迎留言交流，分享你的想法和建议' },
        },
        {
          path: 'ai-chat',
          name: 'ai-chat',
          component: () => import('@/views/ChatView.vue'),
          meta: { title: 'AI 对话', requiresAuth: true, description: '与 AI 助手进行技术对话' },
        },
        {
          path: 'stats',
          name: 'stats',
          component: () => import('@/views/StatsView.vue'),
          meta: { title: '站点统计', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: ':pathMatch(.*)*',
          name: 'not-found',
          component: () => import('@/views/NotFoundView.vue'),
          meta: { title: '页面不存在' },
        },
      ],
    },
  ],
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

// Auth guard
router.beforeEach(async (to, _from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.requiresAdmin) {
    if (!token) {
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
    try {
      const { getProfile } = await import('@/api/auth')
      const user = await getProfile()
      if (user.role !== 'super_admin') {
        next({ name: 'home' })
        return
      }
    } catch {
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
  }

  next()
})

// 动态更新页面标题 + SEO meta tags
router.afterEach((to) => {
  const base = 'minlan01'
  const pageTitle = to.meta.title as string | undefined
  const fullTitle = pageTitle ? `${pageTitle} — ${base}` : base
  document.title = fullTitle

  // Update meta tags
  const description = to.meta.description as string | undefined
  setMeta('name', 'description', description || '一个技术博客')
  setMeta('property', 'og:title', fullTitle)
  setMeta('property', 'og:description', description || '一个技术博客')
  setMeta('property', 'og:url', `${window.location.origin}${to.path}`)
  setMeta('property', 'og:type', 'website')
  setMeta('property', 'og:site_name', base)
  setMeta('name', 'twitter:card', 'summary_large_image')
  setMeta('name', 'twitter:title', fullTitle)
  setMeta('name', 'twitter:description', description || '一个技术博客')
})

function setMeta(attr: string, key: string, content: string) {
  let el = document.querySelector(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

export default router
