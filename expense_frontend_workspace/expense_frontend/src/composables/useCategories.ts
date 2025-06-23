import { ref } from 'vue'
import { api } from '../services/api'

interface CategoryItem {
  id: number
  name: string
  color?: string
  [key: string]: unknown
}

const categories = ref<CategoryItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

export function useCategories() {
  async function fetchCategories() {
    loading.value = true
    error.value = null
    try {
      const resp = await api.get<CategoryItem[]>('/categories')
      categories.value = resp.data
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } }
      error.value = err.response?.data?.detail || 'Failed to load categories'
    } finally {
      loading.value = false
    }
  }

  async function addCategory(data: Omit<CategoryItem, 'id'>) {
    loading.value = true
    error.value = null
    try {
      const resp = await api.post<CategoryItem>('/categories', data)
      categories.value.push(resp.data)
      return resp.data
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } }
      error.value = err.response?.data?.detail || 'Failed to add category'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateCategory(id: number, data: Partial<Omit<CategoryItem, 'id'>>) {
    loading.value = true
    error.value = null
    try {
      const resp = await api.put<CategoryItem>(`/categories/${id}`, data)
      const idx = categories.value.findIndex((c) => c.id === id)
      if (idx > -1) categories.value[idx] = resp.data
      return resp.data
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } }
      error.value = err.response?.data?.detail || 'Failed to update category'
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteCategory(id: number) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/categories/${id}`)
      categories.value = categories.value.filter((c) => c.id !== id)
      return true
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } }
      error.value = err.response?.data?.detail || 'Failed to delete category'
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    categories,
    loading,
    error,
    fetchCategories,
    addCategory,
    updateCategory,
    deleteCategory,
  }
}
