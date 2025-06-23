import { ref } from 'vue'
import { api, setAuthToken, clearAuthToken } from '../services/api'

const user = ref(null)
const isAuthenticated = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)

// PUBLIC_INTERFACE
export function useAuth() {
  // Try to restore session from localStorage
  if (!user.value && localStorage.getItem('user')) {
    user.value = JSON.parse(localStorage.getItem('user')!)
    setAuthToken(localStorage.getItem('token')!)
    isAuthenticated.value = true
  }

  // PUBLIC_INTERFACE
  async function login(email: string, password: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const resp = await api.post('/auth/login', { email, password })
      user.value = resp.data.user
      isAuthenticated.value = true
      setAuthToken(resp.data.access_token)
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('token', resp.data.access_token)
      return true
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } }
      error.value = err.response?.data?.detail || 'Login failed'
      isAuthenticated.value = false
      return false
    } finally {
      loading.value = false
    }
  }

  // PUBLIC_INTERFACE
  async function register(email: string, password: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      await api.post('/auth/register', { email, password })
      return await login(email, password)
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } }
      error.value = err.response?.data?.detail || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  // PUBLIC_INTERFACE
  function logout() {
    clearAuthToken()
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  return {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    logout,
    register,
  }
}
