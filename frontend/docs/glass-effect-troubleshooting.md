# 毛玻璃效果调试记录

> 日期：2026-04-21
> 涉及文件：`base.css`、`variables.css`、`DefaultLayout.vue`、`AnimatedBackground.vue`、`OpeningScreen.vue`

---

## 背景

博客前端使用 "Frosted Glass Dark" 主题，所有页面的内容面板需要呈现毛玻璃效果：
- 面板微微透光，能透过面板看到背景的代码雨动画
- 代码雨经过 `backdrop-filter: blur()` 产生模糊扩散效果
- 涉及页面：归档、文章列表、文章详情、留言板、友链、AI、关于等

---

## 问题一：开屏动画（Opening Screen）不消失

### 现象
首页进入后，开屏动画没有显示，也没有 ENTER 按钮，鼠标滚轮滑动直接到页脚。用户无法进入主内容区域。

### 排查
在浏览器控制台执行诊断：
```js
document.querySelector('.home__body')  // → null（NOT FOUND）
document.querySelector('.opening')     // → 元素存在（开屏卡住了）
```

### 根因
`base.css` 中的 `.page-enter` 动画使用了 `animation-fill-mode: both`：
```css
.page-enter {
  animation: pageSlideIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes pageSlideIn {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

`transform: translateY(0)` 通过 `both` 填充模式永久生效，根据 CSS 规范创建了一个新的包含块（containing block），导致 OpeningScreen 组件的 `position: fixed` 不再相对于视口定位，而是相对于带有 `transform` 的父元素。

### 修复
在 `HomeView.vue` 中用 `<Teleport to="body">` 包裹 OpeningScreen：
```html
<Teleport to="body">
  <OpeningScreen v-if="showOpening" ... @enter="onEnter" />
</Teleport>
```

---

## 问题二：代码雨只显示一半

### 现象
开屏动画修复后，背景的 Matrix 代码雨只渲染在上半屏。

### 根因
OpeningScreen.vue 中 `.opening` 类使用了 `overflow: auto`，在内容溢出时触发了滚动行为。

### 修复
```css
.opening { overflow: hidden; }  /* 原来是 overflow: auto */
```

---

## 问题三：毛玻璃效果不生效（核心问题）

### 现象
将面板背景改为半透明（`rgba(10, 10, 20, 0.35)`）并添加 `backdrop-filter: blur(16px)` 后：
- HMR 热更新时效果短暂出现
- 刷新页面后效果消失
- 浏览器确认 CSS 变量值正确（`rgba(10, 10, 20, 0.35)`）
- `backdrop-filter` 声明存在于计算样式中
- 所有页面的面板看起来都是纯透明的

### 排查过程

1. **确认 CSS 变量正确**：在控制台检查 `getComputedStyle` 确认变量值已更新
2. **确认 Vite 服务正确**：重启 dev server，确认无 504 Outdated Dep 错误
3. **确认选择器匹配**：`.shell__main .container` 选择器匹配到所有视图的容器元素
4. **确认 backdrop-filter 声明存在**：`!important` + `-webkit-` 前缀都正确
5. **排除 ::before 伪元素干扰**：噪点纹理 opacity 仅 0.04，不会遮挡效果

### 根因

`backdrop-filter` 的工作原理是采样元素背后的渲染内容进行模糊。但浏览器使用**合成层（compositing layer）**来优化渲染：

```
DOM 层级：
body → #app → .shell → .shell__main → [.page-enter] → .container（有 backdrop-filter）
                                  ↖
                    AnimatedBackground（fixed, z-index: 0）← 不同合成层
```

关键问题链：
1. `.page-enter` 的 CSS `animation` 属性（即使动画已完成）让浏览器为该元素保持了独立的合成层
2. 这个合成层将 `.container` 与背景画布（AnimatedBackground）隔离
3. `backdrop-filter` 只能在同一合成层内采样 → 采样到的是透明/空内容
4. 结果：面板看起来完全透明，没有模糊效果

### 修复方案（三步）

#### 步骤一：替换 CSS animation 为 Vue Transition

**DefaultLayout.vue** — 用 Vue `<Transition>` 替换 CSS 动画类：
```html
<!-- 之前 -->
<component :is="Component" :key="route.path" class="page-enter" />

<!-- 之后 -->
<Transition name="page-fade" mode="out-in">
  <component :is="Component" :key="route.path" />
</Transition>
```

**base.css** — 替换动画为过渡类：
```css
/* 之前：CSS animation 会永久保留合成层 */
.page-enter {
  animation: pageSlideIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
}

/* 之后：Vue Transition 类在过渡完成后被移除 */
.page-fade-enter-active { transition: opacity 0.4s ease 0.15s; }
.page-fade-leave-active { transition: opacity 0.25s ease; }
.page-fade-enter-from,
.page-fade-leave-to { opacity: 0; }
```

Vue Transition 的关键优势：过渡完成后，`*-enter-active` 等类会从 DOM 元素上移除，不会留下任何创建合成层的 CSS 属性。

#### 步骤二：修复 body 背景

```css
/* 之前 */
body { background: transparent; }

/* 之后 */
body { background: var(--color-bg-deep); }
```

`background: transparent` 意味着 `backdrop-filter` 在最底层采样到的可能是空白。

#### 步骤三：增亮代码雨

```javascript
// AnimatedBackground.vue
// 头部字符 0.35 → 0.5，尾迹 0.16 → 0.25
ctx.fillStyle = 'rgba(0, 255, 65, 0.5)'   // 更亮
ctx.fillStyle = 'rgba(0, 255, 65, 0.25)'  // 更亮
```

代码雨经过 `blur(16px)` 后亮度会大幅扩散衰减，需要更亮的原始亮度才能在毛玻璃面板后产生可见的模糊辉光。

---

## 技术要点总结

### 什么会阻断 backdrop-filter？

以下 CSS 属性在**祖先元素**上使用时，会创建合成层/层叠上下文，可能阻断 `backdrop-filter` 跨层采样：

| 属性 | 影响方式 |
|------|---------|
| `transform: any` | 创建新合成层 |
| `filter: any` | 创建新合成层 |
| `opacity < 1` | 创建层叠上下文 |
| `will-change: transform/opacity` | 提示浏览器创建合成层 |
| `position: fixed` + `z-index` | 创建独立合成层 |
| `animation` (with fill-mode) | 动画完成后可能保留合成层 |

### 最佳实践

1. **避免在 backdrop-filter 元素的祖先上使用动画**：用 Vue Transition 替代 CSS animation
2. **确保 body 有实际背景色**：不要使用 `background: transparent`
3. **背景画布与内容在同一合成层**：避免 `position: fixed` + `z-index` 创建隔离
4. **测试方法**：在面板后放一个亮色元素，如果看不到模糊效果则 `backdrop-filter` 未生效

---

## 相关文件清单

| 文件 | 修改内容 |
|------|---------|
| `src/assets/styles/base.css` | 替换 animation → transition，修复 body 背景 |
| `src/assets/styles/variables.css` | 毛玻璃变量（透明度、模糊值） |
| `src/layouts/DefaultLayout.vue` | Vue Transition 替代 CSS class 动画 |
| `src/components/common/AnimatedBackground.vue` | 代码雨亮度增强 |
| `src/components/landing/OpeningScreen.vue` | overflow 修复 |
| `src/views/HomeView.vue` | Teleport 包裹 OpeningScreen |
