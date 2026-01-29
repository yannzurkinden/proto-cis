import apiClient from './client'
import type { PAI } from '@/types/api'

export interface PAIFormData {
  title?: string
  valid_from: string
  valid_to?: string | null
  strengths?: string | null
  difficulties?: string | null
  beneficiary_wishes?: string | null
  objectives?: Array<{
    title: string
    description?: string
    objective_type: string
    term: string
    priority: string
    due_date?: string | null
    indicators?: Array<{ description: string }>
    actions?: Array<{ description: string; responsible?: string; due_date?: string | null }>
  }>
}

export const paisApi = {
  get: async (beneficiaryId: number, paiId: number): Promise<PAI> => {
    const response = await apiClient.get<PAI>(`/beneficiaries/${beneficiaryId}/pais/${paiId}`)
    return response.data
  },

  list: async (beneficiaryId: number, status?: string): Promise<PAI[]> => {
    const response = await apiClient.get<PAI[]>(`/beneficiaries/${beneficiaryId}/pais`, {
      params: { status },
    })
    return response.data
  },

  create: async (beneficiaryId: number, data: PAIFormData): Promise<PAI> => {
    const response = await apiClient.post<PAI>(`/beneficiaries/${beneficiaryId}/pais`, data)
    return response.data
  },

  update: async (beneficiaryId: number, paiId: number, data: PAIFormData): Promise<PAI> => {
    const response = await apiClient.put<PAI>(`/beneficiaries/${beneficiaryId}/pais/${paiId}`, data)
    return response.data
  },

  activate: async (beneficiaryId: number, paiId: number): Promise<PAI> => {
    const response = await apiClient.post<PAI>(`/beneficiaries/${beneficiaryId}/pais/${paiId}/activate`)
    return response.data
  },

  close: async (beneficiaryId: number, paiId: number): Promise<PAI> => {
    const response = await apiClient.post<PAI>(`/beneficiaries/${beneficiaryId}/pais/${paiId}/close`)
    return response.data
  },
}
