import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001'

// PUBLIC_INTERFACE
export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // for cookie-based auth if used
})

// PUBLIC_INTERFACE
export function setAuthToken(token: string) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// PUBLIC_INTERFACE
export function clearAuthToken() {
  delete api.defaults.headers.common['Authorization']
}
