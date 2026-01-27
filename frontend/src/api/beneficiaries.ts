import apiClient from './client'
import type { Beneficiary, BeneficiaryListItem, PaginatedResponse, Contact } from '@/types/api'

export interface BeneficiaryFilters {
  page?: number
  size?: number
  status?: string
  unit_id?: number
  referent_id?: number
  search?: string
  sort?: string
}

export const beneficiariesApi = {
  list: async (filters: BeneficiaryFilters = {}): Promise<PaginatedResponse<BeneficiaryListItem>> => {
    const response = await apiClient.get<PaginatedResponse<BeneficiaryListItem>>('/beneficiaries', {
      params: filters,
    })
    return response.data
  },

  get: async (id: number): Promise<Beneficiary> => {
    const response = await apiClient.get<Beneficiary>(`/beneficiaries/${id}`)
    return response.data
  },

  create: async (data: Partial<Beneficiary>): Promise<Beneficiary> => {
    const response = await apiClient.post<Beneficiary>('/beneficiaries', data)
    return response.data
  },

  update: async (id: number, data: Partial<Beneficiary>): Promise<Beneficiary> => {
    const response = await apiClient.put<Beneficiary>(`/beneficiaries/${id}`, data)
    return response.data
  },

  // Medical data
  getMedicalData: async (id: number) => {
    const response = await apiClient.get(`/beneficiaries/${id}/medical`)
    return response.data
  },

  updateMedicalData: async (id: number, data: Record<string, string>) => {
    const response = await apiClient.put(`/beneficiaries/${id}/medical`, data)
    return response.data
  },

  // Contacts
  getContacts: async (id: number): Promise<Contact[]> => {
    const response = await apiClient.get<Contact[]>(`/beneficiaries/${id}/contacts`)
    return response.data
  },

  createContact: async (beneficiaryId: number, data: Partial<Contact>): Promise<Contact> => {
    const response = await apiClient.post<Contact>(`/beneficiaries/${beneficiaryId}/contacts`, data)
    return response.data
  },

  updateContact: async (beneficiaryId: number, contactId: number, data: Partial<Contact>): Promise<Contact> => {
    const response = await apiClient.put<Contact>(`/beneficiaries/${beneficiaryId}/contacts/${contactId}`, data)
    return response.data
  },

  deleteContact: async (beneficiaryId: number, contactId: number): Promise<void> => {
    await apiClient.delete(`/beneficiaries/${beneficiaryId}/contacts/${contactId}`)
  },

  // PAIs
  getPAIs: async (beneficiaryId: number, status?: string) => {
    const response = await apiClient.get(`/beneficiaries/${beneficiaryId}/pais`, {
      params: { status },
    })
    return response.data
  },

  createPAI: async (beneficiaryId: number, data: Record<string, unknown>) => {
    const response = await apiClient.post(`/beneficiaries/${beneficiaryId}/pais`, data)
    return response.data
  },
}
