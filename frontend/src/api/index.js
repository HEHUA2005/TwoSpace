import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
})

api.interceptors.request.use(config => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
      // 用 router 跳转避免整页刷新闪白；若 router 不可用则降级
      import('../router').then(({ default: router }) => router.replace('/login'))
    }
    return Promise.reject(err)
  }
)

export default api
