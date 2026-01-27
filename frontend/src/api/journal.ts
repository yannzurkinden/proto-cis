import apiClient from './client'
import type { JournalEntry, JournalCategory, PaginatedResponse } from '@/types/api'

export interface JournalFilters {
  page?: number
  size?: number
  beneficiary_id?: number
  author_id?: number
  category?: string
  date_from?: string
  date_to?: string
  search?: string
  tags?: string
}

export const journalApi = {
  list: async (filters: JournalFilters = {}): Promise<PaginatedResponse<JournalEntry>> => {
    const response = await apiClient.get<PaginatedResponse<JournalEntry>>('/journal', {
      params: filters,
    })
    return response.data
  },

  get: async (id: number): Promise<JournalEntry> => {
    const response = await apiClient.get<JournalEntry>(`/journal/${id}`)
    return response.data
  },

  create: async (data: {
    beneficiary_id: number
    title: string
    content: string
    entry_date?: string
    visibility?: string
    category_ids: number[]
    tags: string[]
  }): Promise<JournalEntry> => {
    const response = await apiClient.post<JournalEntry>('/journal', data)
    return response.data
  },

  update: async (id: number, data: Partial<JournalEntry> & {
    category_ids?: number[]
    tags?: string[]
  }): Promise<JournalEntry> => {
    const response = await apiClient.put<JournalEntry>(`/journal/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/journal/${id}`)
  },

  getCategories: async (): Promise<JournalCategory[]> => {
    const response = await apiClient.get<JournalCategory[]>('/journal/categories')
    return response.data
  },

  getTags: async (beneficiaryId?: number): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/journal/tags', {
      params: { beneficiary_id: beneficiaryId },
    })
    return response.data
  },
}
