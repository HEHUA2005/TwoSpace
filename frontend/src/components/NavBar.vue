<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter, useRoute } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const navItems = [
  { path: '/',            label: '首页',   icon: '🏠' },
  { path: '/diary',       label: '日记',   icon: '📖' },
  { path: '/gallery',     label: '相册',   icon: '🖼' },
  { path: '/anniversary', label: '纪念日', icon: '🎂' },
]

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar">
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
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background: rgba(255, 249, 251, 0.95);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid #f9d4e5;
  gap: 24px;
}
.brand {
  font-size: 18px;
  font-weight: 700;
  color: var(--pink-dark);
  white-space: nowrap;
}
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
}
.user-name { font-size: 13px; color: var(--text-muted); }
.logout-btn { padding: 5px 12px; font-size: 13px; }
</style>
