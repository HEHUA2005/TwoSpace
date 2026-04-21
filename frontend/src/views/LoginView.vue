<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const auth = useAuthStore()

const users = ref([])
const selectedUser = ref(null)
const password = ref('')
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

onMounted(async () => {
  const { data } = await api.get('/auth/users')
  users.value = data
})

function selectUser(u) {
  selectedUser.value = u
  password.value = ''
  error.value = ''
}

async function submit() {
  if (!selectedUser.value || !password.value) return
  loading.value = true
  error.value = ''
  try {
    await auth.login(selectedUser.value.id, password.value)
    router.push('/')
  } catch {
    error.value = '密码错误，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrap">
    <div class="login-card card">
      <div class="logo">💕</div>
      <h1>TwoSpace</h1>
      <p class="subtitle">我们的小世界</p>

      <!-- 选择用户 -->
      <div v-if="!selectedUser" class="user-list">
        <p class="hint">你是谁？</p>
        <div class="avatars">
          <button
            v-for="u in users"
            :key="u.id"
            class="avatar-btn"
            @click="selectUser(u)"
          >
            <img :src="u.avatar" :alt="u.name" @error="e => e.target.src='/default-avatar.png'" />
            <span>{{ u.name }}</span>
          </button>
        </div>
      </div>

      <!-- 输入密码 -->
      <div v-else class="password-form">
        <button class="back-btn" @click="selectedUser = null">← 返回</button>
        <div class="selected-user">
          <img :src="selectedUser.avatar" :alt="selectedUser.name" @error="e => e.target.src='/default-avatar.png'" />
          <span>{{ selectedUser.name }}</span>
        </div>
        <div class="input-wrap">
          <input
            :type="showPassword ? 'text' : 'password'"
            v-model="password"
            placeholder="输入密码"
            @keyup.enter="submit"
            autofocus
          />
          <button class="toggle-pw" @click="showPassword = !showPassword">
            {{ showPassword ? '🙈' : '👁' }}
          </button>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn btn-primary login-btn" @click="submit" :disabled="loading">
          {{ loading ? '登录中...' : '进入' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fde8f1 0%, #fff9fb 100%);
}
.login-card {
  width: 360px;
  text-align: center;
  padding: 40px 32px;
}
.logo { font-size: 48px; margin-bottom: 8px; }
h1 { font-size: 28px; color: var(--pink-dark); font-weight: 700; }
.subtitle { color: var(--text-muted); margin-top: 4px; margin-bottom: 32px; }
.hint { color: var(--text-muted); font-size: 14px; margin-bottom: 20px; }
.avatars { display: flex; justify-content: center; gap: 32px; }
.avatar-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  background: none;
  padding: 16px;
  border-radius: var(--radius);
  transition: all 0.2s;
}
.avatar-btn:hover {
  background: var(--pink-light);
  transform: translateY(-3px);
}
.avatar-btn img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--pink);
}
.avatar-btn span { font-size: 15px; font-weight: 500; }

.password-form { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.back-btn { background: none; color: var(--text-muted); font-size: 14px; align-self: flex-start; }
.selected-user {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.selected-user img {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--pink);
}
.selected-user span { font-weight: 500; }
.input-wrap { position: relative; width: 100%; }
.input-wrap input { padding-right: 40px; }
.toggle-pw {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  font-size: 16px;
}
.error { color: #dc2626; font-size: 13px; }
.login-btn { width: 100%; justify-content: center; padding: 12px; font-size: 16px; }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
