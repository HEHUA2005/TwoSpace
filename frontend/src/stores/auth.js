import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('ts_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('ts_user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  async function login(userId, password) {
    const { data } = await api.post('/auth/login', { user_id: userId, password })
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('ts_token', data.access_token)
    localStorage.setItem('ts_user', JSON.stringify(data.user))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('ts_token')
    localStorage.removeItem('ts_user')
  }

  return { token, user, isLoggedIn, login, logout }
})
