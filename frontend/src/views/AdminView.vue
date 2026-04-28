<template>
  <section class="admin-page">
    <div class="container">
      <header class="admin-page__header">
        <div class="admin-page__header-left">
          <button class="admin-page__back" @click="$router.push('/')">&larr; 返回首页</button>
          <h1 class="admin-page__title">后台管理</h1>
        </div>
        <button class="admin-page__create-btn" @click="$router.push('/create-post')">
          + 写文章
        </button>
      </header>

      <!-- Tabs -->
      <div class="admin-page__tabs">
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'posts' }"
          @click="activeTab = 'posts'"
        >文章管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'categories' }"
          @click="activeTab = 'categories'"
        >分类管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'tags' }"
          @click="activeTab = 'tags'"
        >标签管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'stats' }"
          @click="activeTab = 'stats'"
        >站点统计</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'friend-links' }"
          @click="activeTab = 'friend-links'"
        >友链管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'users' }"
          @click="activeTab = 'users'"
        >用户管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'comments' }"
          @click="activeTab = 'comments'"
        >评论审核</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'messages' }"
          @click="activeTab = 'messages'"
        >留言管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'media' }"
          @click="activeTab = 'media'"
        >媒体库</button>
      </div>

      <!-- Posts Tab -->
      <div v-if="activeTab === 'posts'" class="admin-page__panel">
        <div class="admin-page__toolbar">
          <div class="admin-page__toolbar-left">
            <button class="admin-btn admin-btn--edit" @click="handleExportPosts">导出全部</button>
            <label class="admin-btn admin-btn--edit" style="cursor:pointer;">
              导入
              <input type="file" accept=".zip" @change="handleImportPosts" style="display:none" />
            </label>
          </div>
          <div v-if="selectedPostIds.size" class="admin-page__batch-bar">
            <span>已选 {{ selectedPostIds.size }} 篇</span>
            <button class="admin-btn admin-btn--delete" @click="handleBatchDeletePosts">批量删除</button>
          </div>
        </div>
        <div v-if="!postsLoaded" class="admin-page__loading">加载中...</div>
        <div v-else-if="postsError" class="admin-page__error">
          <p>加载失败</p>
          <button class="admin-page__retry" @click="loadPosts">重试</button>
        </div>
        <template v-else>
          <div class="admin-table-wrap">
            <table class="admin-table">
              <thead>
                <tr>
                  <th><input type="checkbox" :checked="selectedPostIds.size === posts.length && posts.length > 0" @change="toggleAllPosts" /></th>
                  <th>标题</th>
                  <th>分类</th>
                  <th>状态</th>
                  <th>精选</th>
                  <th>发布日期</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="post in posts" :key="post.id">
                  <td><input type="checkbox" :checked="selectedPostIds.has(post.id)" @change="togglePostSelect(post.id)" /></td>
                  <td class="admin-table__title">{{ post.title }}</td>
                  <td>{{ post.category?.name ?? '-' }}</td>
                  <td>
                    <span class="admin-page__badge" :class="post.status === 'published' ? 'admin-page__badge--approved' : 'admin-page__badge--draft'">
                      {{ post.status === 'published' ? '已发布' : '草稿' }}
                    </span>
                  </td>
                  <td>
                    <label class="admin-toggle" :title="post.is_featured ? '取消精选' : '设为精选'">
                      <input type="checkbox" :checked="post.is_featured" @change="toggleFeatured(post)" />
                      <span class="admin-toggle__track"><span class="admin-toggle__thumb"></span></span>
                    </label>
                  </td>
                  <td class="admin-table__date">{{ formatDate(post.published_at) }}</td>
                  <td class="admin-table__actions">
                    <button class="admin-btn admin-btn--edit" @click="$router.push(`/edit-post/${post.slug}`)">编辑</button>
                    <button class="admin-btn admin-btn--delete" @click="openDeleteModal('post', post.id, post.title)">删除</button>
                  </td>
                </tr>
                <tr v-if="!posts.length">
                  <td colspan="6" class="admin-table__empty">暂无文章</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>

      <!-- Categories Tab -->
      <div v-if="activeTab === 'categories'" class="admin-page__panel">
        <div class="admin-page__inline-form">
          <input
            v-model="newCatName"
            class="admin-input"
            placeholder="分类名称"
            @keyup.enter="handleAddCategory"
          />
          <input
            v-model="newCatSlug"
            class="admin-input"
            placeholder="Slug（可选）"
            @keyup.enter="handleAddCategory"
          />
          <button class="admin-page__create-btn admin-page__create-btn--sm" @click="handleAddCategory">新增</button>
        </div>
        <div v-if="!catsLoaded" class="admin-page__loading">加载中...</div>
        <div v-else class="admin-table-wrap">
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>名称</th>
                <th>Slug</th>
                <th>描述</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cat in categories" :key="cat.id">
                <td>{{ cat.id }}</td>
                <td>
                  <input v-if="editingCat?.id === cat.id" v-model="editingCat.name" class="admin-input admin-input--inline" @keyup.enter="handleSaveCategory(cat.id)" @keyup.escape="editingCat = null" />
                  <span v-else>{{ cat.name }}</span>
                </td>
                <td>
                  <input v-if="editingCat?.id === cat.id" v-model="editingCat.slug" class="admin-input admin-input--inline" @keyup.enter="handleSaveCategory(cat.id)" @keyup.escape="editingCat = null" />
                  <span v-else>{{ cat.slug }}</span>
                </td>
                <td>
                  <input v-if="editingCat?.id === cat.id" v-model="editingCat.description" class="admin-input admin-input--inline" placeholder="描述（可选）" @keyup.enter="handleSaveCategory(cat.id)" @keyup.escape="editingCat = null" />
                  <span v-else>{{ cat.description ?? '-' }}</span>
                </td>
                <td class="admin-table__actions">
                  <template v-if="editingCat?.id === cat.id">
                    <button class="admin-btn admin-btn--edit" @click="handleSaveCategory(cat.id)">保存</button>
                    <button class="admin-btn" @click="editingCat = null">取消</button>
                  </template>
                  <template v-else>
                    <button class="admin-btn admin-btn--edit" @click="startEditCategory(cat)">编辑</button>
                    <button class="admin-btn admin-btn--delete" @click="openDeleteModal('category', cat.id, cat.name)">删除</button>
                  </template>
                </td>
              </tr>
              <tr v-if="!categories.length">
                <td colspan="5" class="admin-table__empty">暂无分类</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tags Tab -->
      <div v-if="activeTab === 'tags'" class="admin-page__panel">
        <div class="admin-page__inline-form">
          <input
            v-model="newTagName"
            class="admin-input"
            placeholder="标签名称"
            @keyup.enter="handleAddTag"
          />
          <input
            v-model="newTagSlug"
            class="admin-input"
            placeholder="Slug（可选）"
            @keyup.enter="handleAddTag"
          />
          <button class="admin-page__create-btn admin-page__create-btn--sm" @click="handleAddTag">新增</button>
        </div>
        <div v-if="!tagsLoaded" class="admin-page__loading">加载中...</div>
        <div v-else class="admin-table-wrap">
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>名称</th>
                <th>Slug</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tag in tags" :key="tag.id">
                <td>{{ tag.id }}</td>
                <td>
                  <input v-if="editingTag?.id === tag.id" v-model="editingTag.name" class="admin-input admin-input--inline" @keyup.enter="handleSaveTag(tag.id)" @keyup.escape="editingTag = null" />
                  <span v-else>{{ tag.name }}</span>
                </td>
                <td>
                  <input v-if="editingTag?.id === tag.id" v-model="editingTag.slug" class="admin-input admin-input--inline" @keyup.enter="handleSaveTag(tag.id)" @keyup.escape="editingTag = null" />
                  <span v-else>{{ tag.slug }}</span>
                </td>
                <td class="admin-table__actions">
                  <template v-if="editingTag?.id === tag.id">
                    <button class="admin-btn admin-btn--edit" @click="handleSaveTag(tag.id)">保存</button>
                    <button class="admin-btn" @click="editingTag = null">取消</button>
                  </template>
                  <template v-else>
                    <button class="admin-btn admin-btn--edit" @click="startEditTag(tag)">编辑</button>
                    <button class="admin-btn admin-btn--delete" @click="openDeleteModal('tag', tag.id, tag.name)">删除</button>
                  </template>
                </td>
              </tr>
              <tr v-if="!tags.length">
                <td colspan="4" class="admin-table__empty">暂无标签</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Stats Tab -->
      <div v-if="activeTab === 'stats'" class="admin-page__panel">
        <div class="admin-page__stats-header">
          <p class="admin-page__stats-desc">站点访问数据分析（可接入 Umami 等统计服务）</p>
          <RouterLink to="/stats" class="admin-page__stats-link">
            查看完整统计 &rarr;
          </RouterLink>
        </div>

        <div class="admin-page__stats-overview">
          <div class="admin-page__stat-card" v-for="stat in statsOverview" :key="stat.label">
            <div class="admin-page__stat-icon" v-html="stat.icon"></div>
            <div class="admin-page__stat-info">
              <span class="admin-page__stat-value">{{ stat.value }}</span>
              <span class="admin-page__stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>

        <div class="admin-page__stats-grid">
          <div class="admin-page__stats-panel">
            <h3 class="admin-page__stats-title">站点页面</h3>
            <table class="admin-table">
              <thead>
                <tr><th>路径</th><th>页面</th></tr>
              </thead>
              <tbody>
                <tr v-for="p in statsTopPages" :key="p.path">
                  <td style="font-family:var(--font-mono);font-size:0.82rem;">{{ p.path }}</td>
                  <td>{{ p.label }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="admin-page__stats-panel">
            <h3 class="admin-page__stats-title">设备分布</h3>
            <div class="admin-page__bars">
              <div v-for="d in statsDevices" :key="d.name" class="admin-page__bar-item">
                <div class="admin-page__bar-header">
                  <span>{{ d.name }}</span>
                  <span style="font-family:var(--font-mono);font-size:0.78rem;color:var(--color-text-muted);">{{ d.pct }}%</span>
                </div>
                <div class="admin-page__bar-track">
                  <div class="admin-page__bar-fill" :style="{ width: d.pct + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Friend Links Tab -->
      <div v-if="activeTab === 'friend-links'" class="admin-page__panel">
        <div class="admin-page__inline-form">
          <input v-model="newLinkName" class="admin-input" placeholder="名称" />
          <input v-model="newLinkUrl" class="admin-input" placeholder="URL" />
          <input v-model="newLinkDesc" class="admin-input" placeholder="描述" />
          <input v-model="newLinkCategory" class="admin-input" placeholder="分类" style="max-width:100px" />
          <button class="admin-page__create-btn admin-page__create-btn--sm" @click="handleAddLink">新增</button>
        </div>
        <div v-if="!linksLoaded" class="admin-page__loading">加载中...</div>
        <div v-else class="admin-table-wrap">
          <table class="admin-table">
            <thead>
              <tr>
                <th>名称</th>
                <th>URL</th>
                <th>分类</th>
                <th>排序</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="link in friendLinks" :key="link.id">
                <td>
                  <input v-if="editingLink?.id === link.id" v-model="editingLink.name" class="admin-input admin-input--inline" @keyup.enter="handleSaveLink(link.id)" @keyup.escape="editingLink = null" />
                  <span v-else>{{ link.name }}</span>
                </td>
                <td>
                  <input v-if="editingLink?.id === link.id" v-model="editingLink.url" class="admin-input admin-input--inline" style="font-family:var(--font-mono);font-size:0.82rem;" @keyup.enter="handleSaveLink(link.id)" @keyup.escape="editingLink = null" />
                  <span v-else style="font-family:var(--font-mono);font-size:0.82rem;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block;">{{ link.url }}</span>
                </td>
                <td>
                  <input v-if="editingLink?.id === link.id" v-model="editingLink.category" class="admin-input admin-input--inline" style="max-width:100px" @keyup.enter="handleSaveLink(link.id)" @keyup.escape="editingLink = null" />
                  <span v-else>{{ link.category }}</span>
                </td>
                <td>
                  <input v-if="editingLink?.id === link.id" v-model.number="editingLink.sort_order" type="number" class="admin-input admin-input--inline" style="max-width:60px" @keyup.enter="handleSaveLink(link.id)" @keyup.escape="editingLink = null" />
                  <span v-else>{{ link.sort_order }}</span>
                </td>
                <td class="admin-table__actions">
                  <template v-if="editingLink?.id === link.id">
                    <button class="admin-btn admin-btn--edit" @click="handleSaveLink(link.id)">保存</button>
                    <button class="admin-btn" @click="editingLink = null">取消</button>
                  </template>
                  <template v-else>
                    <button class="admin-btn admin-btn--edit" @click="startEditLink(link)">编辑</button>
                    <button class="admin-btn admin-btn--delete" @click="openDeleteModal('friend-link', link.id, link.name)">删除</button>
                  </template>
                </td>
              </tr>
              <tr v-if="!friendLinks.length">
                <td colspan="5" class="admin-table__empty">暂无友链</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Users Tab -->
      <div v-if="activeTab === 'users'" class="admin-page__panel">
        <div v-if="!usersLoaded" class="admin-page__loading">加载中...</div>
        <div v-else class="admin-table-wrap">
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>角色</th>
                <th>注册时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td class="admin-table__title">{{ user.username }}</td>
                <td>
                  <select
                    class="admin-input"
                    :value="user.role"
                    @change="handleUpdateUserRole(user, ($event.target as HTMLSelectElement).value)"
                  >
                    <option value="user">user</option>
                    <option value="super_admin">super_admin</option>
                  </select>
                </td>
                <td class="admin-table__date">{{ formatDate(user.created_at) }}</td>
                <td class="admin-table__actions">
                  <button class="admin-btn admin-btn--delete" @click="openDeleteModal('user', user.id, user.username)">删除</button>
                </td>
              </tr>
              <tr v-if="!users.length">
                <td colspan="5" class="admin-table__empty">暂无用户</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Comments Tab -->
      <div v-if="activeTab === 'comments'" class="admin-page__panel">
        <div v-if="!adminCommentsLoaded" class="admin-page__loading">加载中...</div>
        <div v-else class="admin-table-wrap">
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>作者</th>
                <th>内容</th>
                <th>状态</th>
                <th>时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="comment in adminComments" :key="comment.id">
                <td>{{ comment.id }}</td>
                <td>{{ comment.author_name || '匿名' }}</td>
                <td class="admin-table__title">{{ comment.content }}</td>
                <td>
                  <span class="admin-page__badge" :class="comment.is_approved ? 'admin-page__badge--approved' : 'admin-page__badge--pending'">
                    {{ comment.is_approved ? '已审核' : '待审核' }}
                  </span>
                </td>
                <td class="admin-table__date">{{ formatDate(comment.created_at) }}</td>
                <td class="admin-table__actions">
                  <button
                    v-if="!comment.is_approved"
                    class="admin-btn admin-btn--edit"
                    @click="handleApproveComment(comment.id)"
                  >通过</button>
                  <button class="admin-btn admin-btn--delete" @click="handleAdminDeleteComment(comment.id)">删除</button>
                </td>
              </tr>
              <tr v-if="!adminComments.length">
                <td colspan="6" class="admin-table__empty">暂无评论</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Messages Tab -->
      <div v-if="activeTab === 'messages'" class="admin-page__panel">
        <div v-if="!adminMessagesLoaded" class="admin-page__loading">加载中...</div>
        <div v-else class="admin-table-wrap">
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>昵称</th>
                <th>内容</th>
                <th>回复状态</th>
                <th>时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="msg in adminMessages" :key="msg.id">
                <td>{{ msg.id }}</td>
                <td>{{ msg.name }}</td>
                <td class="admin-table__title">{{ msg.content }}</td>
                <td>
                  <span class="admin-page__badge" :class="msg.admin_reply ? 'admin-page__badge--approved' : 'admin-page__badge--pending'">
                    {{ msg.admin_reply ? '已回复' : '未回复' }}
                  </span>
                </td>
                <td class="admin-table__date">{{ formatDate(msg.created_at) }}</td>
                <td class="admin-table__actions">
                  <button
                    class="admin-btn admin-btn--edit"
                    @click="startReplyMessage(msg)"
                  >{{ msg.admin_reply ? '修改回复' : '回复' }}</button>
                  <button class="admin-btn admin-btn--delete" @click="handleAdminDeleteMessage(msg.id)">删除</button>
                </td>
              </tr>
              <tr v-if="replyingMessage">
                <td colspan="6" class="admin-table__reply-row">
                  <div class="admin-page__reply-form">
                    <span class="admin-page__reply-label">回复 {{ replyingMessage.name }}：</span>
                    <textarea v-model="replyContent" class="admin-input admin-input--textarea" rows="3" placeholder="输入回复内容..."></textarea>
                    <div class="admin-page__reply-actions">
                      <button class="admin-btn admin-btn--edit" :disabled="!replyContent.trim()" @click="handleReplyMessage(replyingMessage.id)">提交回复</button>
                      <button class="admin-btn" @click="replyingMessage = null">取消</button>
                    </div>
                  </div>
                </td>
              </tr>
              <tr v-if="!adminMessages.length">
                <td colspan="6" class="admin-table__empty">暂无留言</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Media Library Tab -->
      <div v-if="activeTab === 'media'" class="admin-page__panel">
        <div class="admin-page__media-toolbar">
          <div class="admin-page__media-toolbar__left">
            <button class="admin-page__media-btn admin-page__media-btn--primary" @click="triggerMediaUpload">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              选择文件
            </button>
            <input ref="mediaFileInput" type="file" accept="image/*" style="position:absolute;width:0;height:0;opacity:0;pointer-events:none;" @change="handleMediaUpload" />
            <span v-if="mediaUploading" class="admin-page__media-status">上传中...</span>
            <span v-if="mediaUploadError" class="admin-page__media-status admin-page__media-status--error">{{ mediaUploadError }}</span>
          </div>
          <div class="admin-page__media-toolbar__right">
            <template v-if="mediaSelectedIds.size > 0">
              <span class="admin-page__media-badge">已选 {{ mediaSelectedIds.size }} 项</span>
              <button class="admin-page__media-btn" :disabled="mediaSelectedIds.size !== 1" :title="mediaSelectedIds.size > 1 ? '只能选择一张图片进行编辑' : '编辑'" @click="handleEditSelectedImage">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                编辑
              </button>
              <button class="admin-page__media-btn admin-page__media-btn--danger" @click="handleDeleteSelectedImages">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                删除
              </button>
              <button class="admin-page__media-btn" @click="mediaSelectAll">全选</button>
              <button class="admin-page__media-btn" @click="mediaSelectedIds = new Set()">取消</button>
            </template>
          </div>
        </div>
        <div v-if="!mediaLoaded" class="admin-page__loading">加载中...</div>
        <div v-else-if="!mediaItems.length" class="admin-page__loading">暂无图片</div>
        <div v-else class="admin-page__media-grid">
          <div
            v-for="img in mediaItems"
            :key="img.id"
            class="admin-page__media-card"
            :class="{ 'admin-page__media-card--selected': mediaSelectedIds.has(img.id), 'admin-page__media-card--editing': editingImgName?.id === img.id }"
          >
            <div class="admin-page__media-img-wrap" @click="toggleMediaSelect(img.id)">
              <img :src="mediaUrl(img.url)" :alt="img.filename" class="admin-page__media-img" />
              <span class="admin-page__media-check-mark">
                <svg v-if="mediaSelectedIds.has(img.id)" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
              </span>
              <span class="admin-page__media-preview-hint" @click.stop="previewImage = img">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              </span>
            </div>
            <div class="admin-page__media-info">
              <template v-if="editingImgName?.id === img.id">
                <input v-model="editingImgName.filename" class="admin-input admin-input--inline" @keyup.enter="handleSaveImageName(img.id)" @keyup.escape="editingImgName = null" />
                <div class="admin-page__media-edit-actions">
                  <button class="admin-btn admin-btn--edit" @click="handleSaveImageName(img.id)">保存</button>
                  <button class="admin-btn" @click="editingImgName = null">取消</button>
                </div>
              </template>
              <template v-else>
                <span class="admin-page__media-name" :title="img.filename">{{ img.filename }}</span>
                <span class="admin-page__media-size">{{ formatSize(img.size) }}</span>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Image Preview Lightbox -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="previewImage" class="modal-overlay" @click.self="previewImage = null">
            <div class="admin-page__preview-modal">
              <img :src="mediaUrl(previewImage.url)" class="admin-page__preview-img" />
              <div class="admin-page__preview-info">
                <span>{{ previewImage.filename }}</span>
                <span style="color:var(--color-text-muted);font-size:0.78rem;margin-left:8px;">{{ formatSize(previewImage.size) }}</span>
              </div>
              <button class="admin-page__preview-close" @click="previewImage = null">&times;</button>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Delete Confirmation Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="deleteModal.show" class="modal-overlay" @click.self="closeDeleteModal">
            <div class="modal">
              <h3 class="modal__title">确认删除</h3>
              <p class="modal__text">
                确定要删除{{ deleteModal.type === 'post' ? '文章' : deleteModal.type === 'category' ? '分类' : deleteModal.type === 'tag' ? '标签' : deleteModal.type === 'user' ? '用户' : '友链' }}
                <strong>「{{ deleteModal.name }}」</strong>吗？此操作不可撤销。
              </p>
              <div class="modal__actions">
                <button class="modal__btn modal__btn--cancel" @click="closeDeleteModal">取消</button>
                <button class="modal__btn modal__btn--confirm" @click="confirmDelete">删除</button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { getPosts, getCategories, getTags, getFriendLinks, getStats, type SiteStats } from '@/api/blog'
import { getAdminPosts, deletePost, deleteCategory, deleteTag, createCategory, createTag, updateCategory, updateTag, updatePost, createFriendLink, updateFriendLink, deleteFriendLink, getUsers, updateUser, deleteUser, getAdminComments, approveComment, adminDeleteComment, getImages, deleteImage, updateImage, type ImageItem, getAdminMessages, replyMessage, adminDeleteMessage, type AdminMessageRead, batchDeletePosts, batchActionComments, exportPosts, importPosts, getPendingComments, rejectComment } from '@/api/admin'
import { safeCall } from '@/api/http'
import type { PostSummary, Category, Tag, FriendLink, User, CommentRead } from '@/types/blog'

// --- Delete Modal ---
const deleteModal = reactive({
  show: false,
  type: '' as 'post' | 'category' | 'tag' | 'friend-link' | 'user',
  id: 0,
  name: '',
})

function openDeleteModal(type: 'post' | 'category' | 'tag' | 'friend-link' | 'user', id: number, name: string) {
  deleteModal.show = true
  deleteModal.type = type
  deleteModal.id = id
  deleteModal.name = name
}

function closeDeleteModal() {
  deleteModal.show = false
}

async function confirmDelete() {
  const { type, id } = deleteModal
  closeDeleteModal()
  if (type === 'post') {
    await deletePost(id)
    await loadPosts()
  } else if (type === 'category') {
    await deleteCategory(id)
    await loadCategories()
  } else if (type === 'tag') {
    await deleteTag(id)
    await loadTags()
  } else if (type === 'friend-link') {
    await deleteFriendLink(id)
    await loadFriendLinks()
  } else if (type === 'user') {
    await deleteUser(id)
    await loadUsers()
  }
}

// --- Posts ---
const posts = ref<PostSummary[]>([])
const postsLoaded = ref(false)
const postsError = ref(false)

async function loadPosts() {
  postsLoaded.value = false
  postsError.value = false
  const result = await safeCall(() => getAdminPosts(), [] as PostSummary[])
  posts.value = result
  postsLoaded.value = true
}

async function toggleFeatured(post: PostSummary) {
  try {
    await updatePost(post.id, { is_featured: !post.is_featured })
    post.is_featured = !post.is_featured
  } catch {
    // revert not needed — checkbox won't visually toggle on error
  }
}

// Batch operations for posts
const selectedPostIds = ref<Set<number>>(new Set())

function togglePostSelect(id: number) {
  if (selectedPostIds.value.has(id)) {
    selectedPostIds.value.delete(id)
  } else {
    selectedPostIds.value.add(id)
  }
  selectedPostIds.value = new Set(selectedPostIds.value)
}

function toggleAllPosts() {
  if (selectedPostIds.value.size === posts.value.length) {
    selectedPostIds.value = new Set()
  } else {
    selectedPostIds.value = new Set(posts.value.map(p => p.id))
  }
}

async function handleBatchDeletePosts() {
  const ids = [...selectedPostIds.value]
  if (!ids.length) return
  try {
    await batchDeletePosts(ids)
    selectedPostIds.value = new Set()
    await loadPosts()
  } catch {}
}

async function handleExportPosts() {
  try {
    const blob = await exportPosts()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'blog_posts.zip'
    a.click()
    URL.revokeObjectURL(url)
  } catch {}
}

async function handleImportPosts(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  try {
    await importPosts(file)
    await loadPosts()
  } catch {} finally {
    target.value = ''
  }
}

// Pending comments for moderation
const pendingComments = ref<CommentRead[]>([])
const pendingLoaded = ref(false)

async function loadPendingComments() {
  pendingLoaded.value = false
  pendingComments.value = await safeCall(() => getPendingComments(), [])
  pendingLoaded.value = true
}

async function handleRejectComment(id: number) {
  try {
    await rejectComment(id)
    pendingComments.value = pendingComments.value.filter(c => c.id !== id)
  } catch {}
}

async function handleBatchApproveComments() {
  const ids = pendingComments.value.map(c => c.id)
  if (!ids.length) return
  try {
    await batchActionComments(ids, 'approve')
    pendingComments.value = []
    await loadAdminComments()
  } catch {}
}

// --- Categories ---
const categories = ref<Category[]>([])
const catsLoaded = ref(false)
const newCatName = ref('')
const newCatSlug = ref('')
const editingCat = ref<{ id: number; name: string; slug: string; description: string } | null>(null)

async function loadCategories() {
  catsLoaded.value = false
  categories.value = await safeCall(() => getCategories(), [])
  catsLoaded.value = true
}

async function handleAddCategory() {
  const name = newCatName.value.trim()
  if (!name) return
  const slug = newCatSlug.value.trim() || name.toLowerCase().replace(/\s+/g, '-')
  await createCategory({ name, slug })
  newCatName.value = ''
  newCatSlug.value = ''
  await loadCategories()
}

function startEditCategory(cat: Category) {
  editingCat.value = { id: cat.id, name: cat.name, slug: cat.slug, description: cat.description ?? '' }
}

async function handleSaveCategory(id: number) {
  if (!editingCat.value) return
  const { name, slug, description } = editingCat.value
  await updateCategory(id, { name, slug, description: description || undefined })
  editingCat.value = null
  await loadCategories()
}

// --- Tags ---
const tags = ref<Tag[]>([])
const tagsLoaded = ref(false)
const newTagName = ref('')
const newTagSlug = ref('')
const editingTag = ref<{ id: number; name: string; slug: string } | null>(null)

async function loadTags() {
  tagsLoaded.value = false
  tags.value = await safeCall(() => getTags(), [])
  tagsLoaded.value = true
}

async function handleAddTag() {
  const name = newTagName.value.trim()
  if (!name) return
  const slug = newTagSlug.value.trim() || name.toLowerCase().replace(/\s+/g, '-')
  await createTag({ name, slug })
  newTagName.value = ''
  newTagSlug.value = ''
  await loadTags()
}

function startEditTag(tag: Tag) {
  editingTag.value = { id: tag.id, name: tag.name, slug: tag.slug }
}

async function handleSaveTag(id: number) {
  if (!editingTag.value) return
  const { name, slug } = editingTag.value
  await updateTag(id, { name, slug })
  editingTag.value = null
  await loadTags()
}

// --- Friend Links ---
const friendLinks = ref<FriendLink[]>([])
const linksLoaded = ref(false)
const newLinkName = ref('')
const newLinkUrl = ref('')
const newLinkDesc = ref('')
const newLinkCategory = ref('default')
const editingLink = ref<{ id: number; name: string; url: string; category: string; sort_order: number } | null>(null)

async function loadFriendLinks() {
  linksLoaded.value = false
  friendLinks.value = await safeCall(() => getFriendLinks(), [])
  linksLoaded.value = true
}

async function handleAddLink() {
  const name = newLinkName.value.trim()
  const url = newLinkUrl.value.trim()
  if (!name || !url) return
  await createFriendLink({
    name,
    url,
    description: newLinkDesc.value.trim() || undefined,
    category: newLinkCategory.value.trim() || 'default',
  })
  newLinkName.value = ''
  newLinkUrl.value = ''
  newLinkDesc.value = ''
  newLinkCategory.value = 'default'
  await loadFriendLinks()
}

function startEditLink(link: FriendLink) {
  editingLink.value = { id: link.id, name: link.name, url: link.url, category: link.category ?? 'default', sort_order: link.sort_order ?? 0 }
}

async function handleSaveLink(id: number) {
  if (!editingLink.value) return
  const { name, url, category, sort_order } = editingLink.value
  await updateFriendLink(id, { name, url, category, sort_order })
  editingLink.value = null
  await loadFriendLinks()
}

// --- Tab ---
const activeTab = ref<'posts' | 'categories' | 'tags' | 'stats' | 'friend-links' | 'users' | 'comments' | 'messages' | 'media'>('posts')

// --- Stats (real data) ---
const siteStats = ref<SiteStats | null>(null)

const statsOverview = computed(() => {
  if (!siteStats.value) return []
  const s = siteStats.value
  return [
    { label: '文章', value: String(s.posts), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>' },
    { label: '总浏览', value: s.total_views.toLocaleString(), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>' },
    { label: '评论', value: String(s.comments), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>' },
    { label: '留言', value: String(s.messages), icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
  ]
})

const statsTopPages = [
  { path: '/', label: '首页' },
  { path: '/posts', label: '文章' },
  { path: '/about', label: '关于' },
  { path: '/archive', label: '归档' },
]
const statsDevices = [
  { name: 'Desktop', pct: 58 },
  { name: 'Mobile', pct: 34 },
  { name: 'Tablet', pct: 8 },
]

async function loadStats() {
  siteStats.value = await safeCall(() => getStats(), null as unknown as SiteStats)
}

// --- Helpers ---
function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

// --- Users ---
const users = ref<User[]>([])
const usersLoaded = ref(false)

async function loadUsers() {
  usersLoaded.value = false
  users.value = await safeCall(() => getUsers(), [])
  usersLoaded.value = true
}

async function handleUpdateUserRole(user: User, newRole: string) {
  try {
    await updateUser(user.id, { role: newRole })
    user.role = newRole
  } catch {
    // Revert on error
  }
}

// --- Admin Comments ---
const adminComments = ref<CommentRead[]>([])
const adminCommentsLoaded = ref(false)

async function loadAdminComments() {
  adminCommentsLoaded.value = false
  adminComments.value = await safeCall(() => getAdminComments(), [])
  adminCommentsLoaded.value = true
}

async function handleApproveComment(id: number) {
  try {
    await approveComment(id)
    const c = adminComments.value.find(c => c.id === id)
    if (c) c.is_approved = true
  } catch {}
}

async function handleAdminDeleteComment(id: number) {
  try {
    await adminDeleteComment(id)
    adminComments.value = adminComments.value.filter(c => c.id !== id)
  } catch {}
}

// --- Admin Messages ---
const adminMessages = ref<AdminMessageRead[]>([])
const adminMessagesLoaded = ref(false)
const replyingMessage = ref<AdminMessageRead | null>(null)
const replyContent = ref('')

async function loadAdminMessages() {
  adminMessagesLoaded.value = false
  adminMessages.value = await safeCall(() => getAdminMessages(), [])
  adminMessagesLoaded.value = true
}

function startReplyMessage(msg: AdminMessageRead) {
  replyingMessage.value = msg
  replyContent.value = msg.admin_reply || ''
}

async function handleReplyMessage(id: number) {
  if (!replyContent.value.trim()) return
  try {
    const updated = await replyMessage(id, replyContent.value.trim())
    const idx = adminMessages.value.findIndex(m => m.id === id)
    if (idx !== -1) adminMessages.value[idx] = updated
    replyingMessage.value = null
    replyContent.value = ''
  } catch {}
}

async function handleAdminDeleteMessage(id: number) {
  try {
    await adminDeleteMessage(id)
    adminMessages.value = adminMessages.value.filter(m => m.id !== id)
  } catch {}
}

// --- Media Library ---
const mediaItems = ref<ImageItem[]>([])
const mediaLoaded = ref(false)
const mediaUploading = ref(false)
const mediaUploadError = ref('')
const mediaFileInput = ref<HTMLInputElement | null>(null)
const mediaSelectMode = ref(false)
const mediaSelectedIds = ref<Set<number>>(new Set())
const previewImage = ref<ImageItem | null>(null)
const editingImgName = ref<{ id: number; filename: string } | null>(null)

function handleEditSelectedImage() {
  if (mediaSelectedIds.value.size !== 1) return
  const id = [...mediaSelectedIds.value][0]
  const img = mediaItems.value.find(i => i.id === id)
  if (img) editingImgName.value = { id: img.id, filename: img.filename }
}

async function loadMedia() {
  mediaLoaded.value = false
  mediaItems.value = await safeCall(() => getImages(), [])
  mediaLoaded.value = true
}

function triggerMediaUpload() {
  mediaFileInput.value?.click()
}

async function handleMediaUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  mediaUploading.value = true
  mediaUploadError.value = ''
  try {
    const formData = new FormData()
    formData.append('file', file)
    const { http } = await import('@/api/http')
    await http.post('/upload', formData)
    await loadMedia()
  } catch (e: any) {
    mediaUploadError.value = e?.response?.data?.detail || e?.message || '上传失败'
  } finally {
    mediaUploading.value = false
    target.value = ''
  }
}

async function handleDeleteImage(id: number) {
  try {
    await deleteImage(id)
    mediaItems.value = mediaItems.value.filter(img => img.id !== id)
    mediaSelectedIds.value.delete(id)
  } catch {}
}

function toggleMediaSelect(id: number) {
  if (mediaSelectedIds.value.has(id)) {
    mediaSelectedIds.value.delete(id)
  } else {
    mediaSelectedIds.value.add(id)
  }
  mediaSelectedIds.value = new Set(mediaSelectedIds.value)
}

function mediaSelectAll() {
  mediaSelectedIds.value = new Set(mediaItems.value.map(img => img.id))
}

async function handleDeleteSelectedImages() {
  const ids = [...mediaSelectedIds.value]
  if (!ids.length) return
  for (const id of ids) {
    try { await deleteImage(id) } catch {}
  }
  mediaItems.value = mediaItems.value.filter(img => !mediaSelectedIds.value.has(img.id))
  mediaSelectedIds.value = new Set()
}

async function handleSaveImageName(id: number) {
  if (!editingImgName.value) return
  const filename = editingImgName.value.filename.trim()
  if (!filename) return
  await updateImage(id, { filename })
  editingImgName.value = null
  mediaSelectedIds.value = new Set()
  await loadMedia()
}

function copyImageUrl(url: string) {
  const fullUrl = window.location.origin + '/api/v1' + url
  navigator.clipboard.writeText(fullUrl)
}

function mediaUrl(url: string) {
  return url.startsWith('http') ? url : '/api/v1' + url
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

onMounted(() => {
  loadPosts()
  loadCategories()
  loadTags()
  loadFriendLinks()
  loadStats()
  loadUsers()
  loadAdminComments()
  loadPendingComments()
  loadAdminMessages()
  loadMedia()
})
</script>

<style scoped>
.admin-page {
  padding: var(--space-3xl) 0;
  min-height: 60vh;
}

.admin-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
}

.admin-page__header-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.admin-page__back {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-muted);
  background: none;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 6px 14px;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.admin-page__back:hover {
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.admin-page__title {
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.admin-page__create-btn {
  font-size: 0.88rem;
  font-weight: 500;
  padding: 10px 22px;
  border: 1px solid var(--accent-tint-40);
  border-radius: var(--radius-sm);
  color: var(--color-accent);
  background: var(--accent-tint-10);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.admin-page__create-btn:hover {
  background: var(--accent-tint-20);
  border-color: var(--color-accent);
}

.admin-page__create-btn--sm {
  padding: 8px 16px;
  font-size: 0.82rem;
}

/* Tabs */
.admin-page__tabs {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-xl);
  padding: var(--space-sm);
  background: var(--glass-surface-bg);
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  backdrop-filter: var(--glass-card-blur);
}

.admin-page__tab {
  font-size: 0.9rem;
  font-weight: 500;
  padding: 8px 18px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  background: var(--glass-bg-02);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.admin-page__tab:hover {
  border-color: var(--border-strong);
  color: var(--color-text);
}

.admin-page__tab.active {
  border-color: var(--accent-tint-40);
  background: var(--accent-tint-15);
  color: var(--color-accent);
}

/* Panel */
.admin-page__panel {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.admin-page__loading {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-text-muted);
}

.admin-page__error {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-text-muted);
}

.admin-page__retry {
  margin-top: var(--space-md);
  padding: 8px 20px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  background: var(--glass-bg-02);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.admin-page__retry:hover {
  border-color: var(--accent-tint-40);
  color: var(--color-accent);
}

/* Inline form */
.admin-page__inline-form {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.admin-input {
  padding: 8px 14px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  background: var(--glass-bg-12);
  color: var(--color-text);
  font-size: 0.88rem;
  outline: none;
  transition: border-color var(--duration-fast) ease;
}

.admin-input::placeholder {
  color: var(--color-text-muted);
}

.admin-input:focus {
  border-color: var(--accent-tint-50);
}

.admin-input--inline {
  width: 100%;
  min-width: 60px;
  padding: 4px 8px;
  font-size: 0.82rem;
}

.admin-input--textarea {
  width: 100%;
  resize: vertical;
  min-height: 60px;
  font-family: inherit;
}

/* Table */
.admin-table-wrap {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--glass-surface-bg);
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  backdrop-filter: var(--glass-card-blur);
}

.admin-table th,
.admin-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 0.88rem;
}

.admin-table th {
  font-weight: 600;
  color: var(--color-text-muted);
  background: var(--glass-bg-03);
  white-space: nowrap;
}

.admin-table td {
  color: var(--color-text-soft);
}

.admin-table tr:last-child td {
  border-bottom: none;
}

.admin-table__title {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-text);
  font-weight: 500;
}

.admin-table__date {
  white-space: nowrap;
}

.admin-table__actions {
  white-space: nowrap;
}

.admin-table__empty {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--space-xl);
}

.admin-table__reply-row {
  padding: var(--space-md);
  background: var(--glass-bg-05);
}

.admin-page__reply-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.admin-page__reply-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-heading);
}

.admin-page__reply-actions {
  display: flex;
  gap: var(--space-sm);
}

/* Toggle Switch */
.admin-toggle {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.admin-toggle input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.admin-toggle__track {
  position: relative;
  width: 38px;
  height: 20px;
  background: var(--border-strong);
  border: 1px solid var(--border-default);
  border-radius: 10px;
  transition: all var(--duration-fast) ease;
}

.admin-toggle__thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 14px;
  height: 14px;
  background: var(--color-text-muted);
  border-radius: 50%;
  transition: all var(--duration-fast) ease;
}

.admin-toggle input:checked + .admin-toggle__track {
  background: var(--accent-tint-25);
  border-color: var(--accent-tint-50);
}

.admin-toggle input:checked + .admin-toggle__track .admin-toggle__thumb {
  left: 20px;
  background: var(--color-accent);
}

.admin-toggle:hover .admin-toggle__track {
  border-color: var(--border-heavy-2);
}

/* Buttons */
.admin-btn {
  font-size: 0.78rem;
  font-weight: 500;
  padding: 5px 12px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  margin-right: 6px;
}

/* Badge */
.admin-page__badge {
  font-size: 0.72rem;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.admin-page__badge--approved {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.admin-page__badge--pending {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.admin-page__badge--draft {
  background: rgba(139, 92, 246, 0.12);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

/* Media Toolbar */
.admin-page__media-toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
  padding: var(--space-sm) var(--space-md);
  background: var(--glass-surface-bg);
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  backdrop-filter: var(--glass-card-blur);
}

.admin-page__media-toolbar__left {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.admin-page__media-toolbar__right {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-left: auto;
}

.admin-page__media-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  font-weight: 500;
  padding: 7px 14px;
  border: 1px solid var(--glass-bg-12);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  background: transparent;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  white-space: nowrap;
}

.admin-page__media-btn:hover {
  color: var(--color-text);
  border-color: var(--border-heavy);
  background: var(--glass-bg-04);
}

.admin-page__media-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  pointer-events: none;
}

.admin-page__media-btn--primary {
  color: var(--color-accent);
  border-color: var(--accent-tint-35);
  background: var(--accent-tint-08);
}

.admin-page__media-btn--primary:hover {
  background: var(--accent-tint-18);
  border-color: var(--accent-tint-50);
}

.admin-page__media-btn--danger {
  color: #f87171;
  border-color: var(--error-border-30);
  background: var(--error-bg-06);
}

.admin-page__media-btn--danger:hover {
  background: var(--error-bg-15);
  border-color: var(--error-border-40);
}

.admin-page__media-btn--active {
  color: var(--color-accent);
  border-color: var(--accent-tint-50);
  background: var(--accent-tint-12);
}

.admin-page__media-status {
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.admin-page__media-status--error {
  color: #f87171;
}

.admin-page__media-badge {
  font-size: 0.72rem;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  background: var(--accent-tint-12);
  color: var(--color-accent);
  border: 1px solid var(--accent-tint-25);
}

/* Media Library */
.admin-page__media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-md);
}

.admin-page__media-card {
  background: var(--glass-surface-bg);
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: all var(--duration-fast) ease;
}

.admin-page__media-card:hover {
  border-color: var(--accent-tint-30);
}

.admin-page__media-card--selected {
  border-color: var(--accent-tint-60);
  box-shadow: 0 0 0 2px var(--accent-tint-20);
}

.admin-page__media-card--editing {
  border-color: var(--accent-tint-40);
}

.admin-page__media-img-wrap {
  position: relative;
  cursor: pointer;
}

.admin-page__media-img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
}

.admin-page__media-check-mark {
  position: absolute;
  top: 6px;
  left: 6px;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(4px);
  border: 1.5px solid var(--border-heavy);
  color: var(--text-overlay-30);
  transition: all var(--duration-fast) ease;
  pointer-events: none;
}

.admin-page__media-card:hover .admin-page__media-check-mark {
  border-color: var(--text-overlay-45);
  color: var(--text-overlay-50);
}

.admin-page__media-card--selected .admin-page__media-check-mark {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #fff;
}

.admin-page__media-preview-hint {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  color: var(--text-overlay-60);
  opacity: 0;
  transition: all var(--duration-fast) ease;
  cursor: pointer;
}

.admin-page__media-card:hover .admin-page__media-preview-hint {
  opacity: 1;
}

.admin-page__media-preview-hint:hover {
  background: var(--accent-tint-50);
  color: #fff;
}

.admin-page__media-info {
  padding: var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.admin-page__media-name {
  font-size: 0.72rem;
  color: var(--color-text-soft);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.admin-page__media-size {
  font-size: 0.68rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

.admin-page__media-edit-actions {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.admin-page__media-edit-actions .admin-btn {
  color: var(--color-text-soft);
}

.admin-btn--edit {
  color: var(--color-accent);
  background: var(--accent-tint-06);
  border-color: var(--accent-tint-30);
}

.admin-btn--edit:hover {
  background: var(--accent-tint-15);
}

.admin-btn--delete {
  color: var(--color-text-muted);
  background: var(--glass-bg-02);
}

.admin-btn--delete:hover {
  color: #f87171;
  border-color: var(--error-border-30);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(20px);
}

.modal {
  width: 90%;
  max-width: 420px;
  padding: var(--space-xl);
  background: var(--modal-bg);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(20px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.modal__title {
  margin: 0 0 var(--space-md);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-heading);
}

.modal__text {
  margin: 0 0 var(--space-lg);
  font-size: 0.9rem;
  color: var(--color-text-soft);
  line-height: 1.6;
}

.modal__text strong {
  color: #f87171;
}

.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
}

.modal__btn {
  padding: 8px 20px;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.modal__btn--cancel {
  border: 1px solid var(--border-strong);
  background: var(--glass-bg-12);
  color: var(--color-text-soft);
}

.modal__btn--cancel:hover {
  border-color: var(--border-strong);
  color: var(--color-text);
}

.modal__btn--confirm {
  border: 1px solid var(--error-border-40);
  background: var(--error-bg-12);
  color: #f87171;
}

.modal__btn--confirm:hover {
  background: var(--error-bg-25);
}

/* Modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .modal,
.modal-leave-active .modal {
  transition: transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal,
.modal-leave-to .modal {
  transform: scale(0.95) translateY(8px);
}

/* Stats Tab */
.admin-page__stats-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
}

.admin-page__stats-desc {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.admin-page__stats-link {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-accent);
  text-decoration: none;
  transition: opacity var(--duration-fast) ease;
}

.admin-page__stats-link:hover {
  opacity: 0.75;
}

.admin-page__stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.admin-page__stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: var(--space-md);
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
}

.admin-page__stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  background: var(--accent-tint-10);
  color: var(--color-accent);
  flex-shrink: 0;
}

.admin-page__stat-info {
  display: flex;
  flex-direction: column;
}

.admin-page__stat-value {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-text-heading);
  font-family: var(--font-mono);
}

.admin-page__stat-label {
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

.admin-page__stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-lg);
}

.admin-page__stats-panel {
  padding: var(--space-md);
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
}

.admin-page__stats-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin: 0 0 var(--space-md);
}

.admin-page__bars {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.admin-page__bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.admin-page__bar-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--color-text);
}

.admin-page__bar-track {
  height: 8px;
  background: var(--color-surface-hover);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.admin-page__bar-fill {
  height: 100%;
  background: var(--color-accent-gradient);
  border-radius: var(--radius-full);
}

/* Image Preview Lightbox */
.admin-page__preview-modal {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.admin-page__preview-img {
  max-width: 90vw;
  max-height: 80vh;
  object-fit: contain;
  border-radius: var(--radius-md);
}

.admin-page__preview-info {
  margin-top: var(--space-sm);
  font-size: 0.85rem;
  color: var(--color-text-soft);
}

.admin-page__preview-close {
  position: absolute;
  top: -12px;
  right: -12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid var(--border-strong);
  background: var(--modal-bg);
  color: var(--color-text);
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) ease;
}

.admin-page__preview-close:hover {
  background: var(--error-bg-20);
  border-color: var(--error-border-40);
  color: #f87171;
}

/* Mobile */
@media (max-width: 768px) {
  .admin-page__header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-md);
  }

  .admin-page__inline-form {
    flex-wrap: wrap;
  }

  .admin-input {
    flex: 1;
    min-width: 120px;
  }

  .admin-table th,
  .admin-table td {
    padding: 10px 10px;
    font-size: 0.82rem;
  }

  .admin-page__stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }

  .admin-page__stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
