import apiClient from './client'
import type { User, Unit, PaginatedResponse } from '@/types/api'
import type { JournalCategory } from '@/types/api'
import type { Skill } from './skills'

export interface AuditLog {
  id: number
  user_id: number
  user_name: string
  action: string
  entity_type: string
  entity_id: number | null
  details: string | null
  ip_address: string | null
  created_at: string
}

export interface CreateUserRequest {
  email: string
  password: string
  first_name: string
  last_name: string
  role: string
  unit_id: number | null
  is_active: boolean
}

export interface UpdateUserRequest {
  first_name?: string
  last_name?: string
  role?: string
  unit_id?: number | null
  is_active?: boolean
}

export const adminApi = {
  // Users
  listUsers: async (params?: {
    page?: number
    size?: number
    role?: string
    unit_id?: number
    is_active?: boolean
    search?: string
  }): Promise<PaginatedResponse<User>> => {
    const response = await apiClient.get<PaginatedResponse<User>>('/admin/users', { params })
    return response.data
  },

  createUser: async (data: CreateUserRequest): Promise<User> => {
    const response = await apiClient.post<User>('/admin/users', data)
    return response.data
  },

  updateUser: async (id: number, data: UpdateUserRequest): Promise<User> => {
    const response = await apiClient.put<User>(`/admin/users/${id}`, data)
    return response.data
  },

  deactivateUser: async (id: number): Promise<void> => {
    await apiClient.post(`/admin/users/${id}/deactivate`)
  },

  // Units
  listUnits: async (): Promise<Unit[]> => {
    const response = await apiClient.get<Unit[]>('/admin/units')
    return response.data
  },

  createUnit: async (data: { name: string; description?: string }): Promise<Unit> => {
    const response = await apiClient.post<Unit>('/admin/units', data)
    return response.data
  },

  updateUnit: async (id: number, data: { name?: string; description?: string }): Promise<Unit> => {
    const response = await apiClient.put<Unit>(`/admin/units/${id}`, data)
    return response.data
  },

  getUnitStats: async (id: number): Promise<{
    beneficiary_count: number
    msp_count: number
  }> => {
    const response = await apiClient.get(`/admin/units/${id}/stats`)
    return response.data
  },

  // Journal categories
  listCategories: async (): Promise<JournalCategory[]> => {
    const response = await apiClient.get<JournalCategory[]>('/admin/journal-categories')
    return response.data
  },

  createCategory: async (data: Partial<JournalCategory>): Promise<JournalCategory> => {
    const response = await apiClient.post<JournalCategory>('/admin/journal-categories', data)
    return response.data
  },

  updateCategory: async (id: number, data: Partial<JournalCategory>): Promise<JournalCategory> => {
    const response = await apiClient.put<JournalCategory>(`/admin/journal-categories/${id}`, data)
    return response.data
  },

  // Skills reference
  listSkills: async (): Promise<Skill[]> => {
    const response = await apiClient.get<Skill[]>('/admin/skills')
    return response.data
  },

  createSkill: async (data: Partial<Skill>): Promise<Skill> => {
    const response = await apiClient.post<Skill>('/admin/skills', data)
    return response.data
  },

  updateSkill: async (id: number, data: Partial<Skill>): Promise<Skill> => {
    const response = await apiClient.put<Skill>(`/admin/skills/${id}`, data)
    return response.data
  },

  deleteSkill: async (id: number): Promise<void> => {
    await apiClient.delete(`/admin/skills/${id}`)
  },

  // Audit logs
  listAuditLogs: async (params?: {
    page?: number
    size?: number
    user_id?: number
    action?: string
    entity_type?: string
    date_from?: string
    date_to?: string
  }): Promise<PaginatedResponse<AuditLog>> => {
    const response = await apiClient.get<PaginatedResponse<AuditLog>>('/admin/audit-logs', {
      params,
    })
    return response.data
  },
}
