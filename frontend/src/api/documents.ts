import apiClient from './client'
import type { Document, PaginatedResponse } from '@/types/api'

export interface DocumentFilters {
  page?: number
  size?: number
  beneficiary_id?: number
  document_type?: string
  confidentiality?: string
  date_from?: string
  date_to?: string
  search?: string
}

export const documentsApi = {
  list: async (filters: DocumentFilters = {}): Promise<PaginatedResponse<Document>> => {
    const response = await apiClient.get<PaginatedResponse<Document>>('/documents', {
      params: filters,
    })
    return response.data
  },

  get: async (id: number): Promise<Document> => {
    const response = await apiClient.get<Document>(`/documents/${id}`)
    return response.data
  },

  upload: async (file: File, metadata: {
    beneficiary_id?: number
    document_type: string
    document_date?: string
    confidentiality?: string
    description?: string
  }): Promise<Document> => {
    const formData = new FormData()
    formData.append('file', file)
    Object.entries(metadata).forEach(([key, value]) => {
      if (value !== undefined) {
        formData.append(key, String(value))
      }
    })
    const response = await apiClient.post<Document>('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  download: async (id: number): Promise<Blob> => {
    const response = await apiClient.get(`/documents/${id}/download`, {
      responseType: 'blob',
    })
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/documents/${id}`)
  },

  getTypes: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/documents/types')
    return response.data
  },
}
