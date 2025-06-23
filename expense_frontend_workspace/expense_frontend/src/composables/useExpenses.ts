import { ref } from 'vue'
import { api } from '../services/api'

interface ExpenseItem {
  id: number
  amount: number
  date: string
  category: string
  description?: string
  [key: string]: unknown
}

const expenses = ref<ExpenseItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

export function useExpenses() {
  async function fetchExpenses(params?: { month?: number; year?: number; category?: string }) {
    loading.value = true
    error.value = null
    try {
      let query = ''
      if (params) {
        const paramsString = Object.entries(params)
          .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
          .join('&')
        query = paramsString ? `?${paramsString}` : ''
      }
      const resp = await api.get<ExpenseItem[]>(`/expenses${query}`)
      expenses.value = resp.data
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } }
      error.value = err.response?.data?.detail || 'Failed to load expenses'
    } finally {
      loading.value = false
    }
  }

  async function addExpense(data: Omit<ExpenseItem, 'id'>) {
    loading.value = true
    error.value = null
    try {
      const resp = await api.post<ExpenseItem>('/expenses', data)
      expenses.value.push(resp.data)
      return resp.data
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } }
      error.value = err.response?.data?.detail || 'Failed to add expense'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateExpense(id: number, data: Partial<Omit<ExpenseItem, 'id'>>) {
    loading.value = true
    error.value = null
    try {
      const resp = await api.put<ExpenseItem>(`/expenses/${id}`, data)
      const idx = expenses.value.findIndex((e) => e.id === id)
      if (idx > -1) expenses.value[idx] = resp.data
      return resp.data
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } }
      error.value = err.response?.data?.detail || 'Failed to update expense'
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteExpense(id: number) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/expenses/${id}`)
      expenses.value = expenses.value.filter((e) => e.id !== id)
      return true
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } }
      error.value = err.response?.data?.detail || 'Failed to delete expense'
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    expenses,
    loading,
    error,
    fetchExpenses,
    addExpense,
    updateExpense,
    deleteExpense,
  }
}
