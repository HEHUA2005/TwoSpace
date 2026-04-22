<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter, useRoute } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const scrolled = ref(false)

function onScroll() {
  scrolled.value = window.scrollY > 60
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

const navItems = [
  { path: '/',        label: '首页',  icon: '🏠' },
  { path: '/diary',   label: '日记',  icon: '📖' },
  { path: '/gallery', label: '相册',  icon: '🖼'  },
  { path: '/stats',   label: 'STATS', icon: '📊' },
]

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <!-- 桌面端顶部导航 -->
  <nav class="navbar" :class="{ scrolled }">
    <RouterLink to="/" class="brand">💕 TwoSpace</RouterLink>
    <div class="nav-links">
      <RouterLink
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: route.path === item.path }"
      >
        <span class="icon">{{ item.icon }}</span>
        <span class="label">{{ item.label }}</span>
      </RouterLink>
    </div>
    <div class="user-area">
      <img
        v-if="auth.user"
        :src="auth.user.avatar"
        :alt="auth.user.name"
        class="user-avatar"
        @error="e => e.target.src='/default-avatar.png'"
      />
      <span class="user-name">{{ auth.user?.name }}</span>
      <button class="btn btn-ghost logout-btn" @click="logout">退出</button>
    </div>
  </nav>

  <!-- 移动端底部 Tab Bar -->
  <nav class="tab-bar">
    <RouterLink
      v-for="item in navItems"
      :key="item.path"
      :to="item.path"
      class="tab-item"
      :class="{ active: route.path === item.path }"
    >
      <span class="tab-icon">{{ item.icon }}</span>
      <span class="tab-label">{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
/* ── 桌面端顶部导航 ── */
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background: rgba(255, 249, 251, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(249, 164, 201, 0.25);
  gap: 24px;
  transition: height 0.3s ease, box-shadow 0.3s ease;
}
.navbar.scrolled {
  height: 48px;
  box-shadow: 0 2px 20px rgba(232, 116, 158, 0.12);
}
.brand {
  font-size: 18px;
  font-weight: 700;
  color: var(--pink-dark);
  white-space: nowrap;
  transition: font-size 0.3s;
}
.navbar.scrolled .brand { font-size: 16px; }
.nav-links {
  display: flex;
  gap: 4px;
  flex: 1;
  justify-content: center;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 14px;
  color: var(--text-muted);
  transition: all 0.2s;
}
.nav-item:hover, .nav-item.active {
  background: var(--pink-light);
  color: var(--pink-dark);
}
.icon { font-size: 16px; }
.user-area {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--pink);
  transition: width 0.3s, height 0.3s;
}
.navbar.scrolled .user-avatar { width: 28px; height: 28px; }
.user-name { font-size: 13px; color: var(--text-muted); }
.logout-btn { padding: 5px 12px; font-size: 13px; }

/* 移动端隐藏顶部导航 */
@media (max-width: 640px) {
  .navbar { display: none; }
}

/* ── 移动端底部 Tab Bar ── */
.tab-bar {
  display: none;
}
@media (max-width: 640px) {
  .tab-bar {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 100;
    background: rgba(255, 249, 251, 0.92);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-top: 1px solid rgba(249, 164, 201, 0.3);
    padding-bottom: env(safe-area-inset-bottom);
  }
  .tab-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 8px 0 6px;
    gap: 3px;
    color: var(--text-muted);
    transition: color 0.2s;
    text-decoration: none;
  }
  .tab-item.active {
    color: var(--pink-dark);
  }
  .tab-icon { font-size: 22px; line-height: 1; }
  .tab-label { font-size: 10px; font-weight: 500; }
}
</style>
