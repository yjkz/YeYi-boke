import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

let refreshPromise: Promise<string> | null = null

const refreshAccessToken = async () => {
  const auth = useAuthStore()
  if (!auth.refreshToken) throw new Error('Missing refresh token')
  if (!refreshPromise) {
    refreshPromise = auth.refresh().finally(() => { refreshPromise = null })
  }
  return refreshPromise
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && original && !original._retry && !String(original.url || '').includes('/auth/refresh')) {
      original._retry = true
      try {
        const token = await refreshAccessToken()
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      } catch {
        const auth = useAuthStore()
        auth.logout()
        router.push('/login')
      }
    }
    return Promise.reject(error)
  },
)

export default api
