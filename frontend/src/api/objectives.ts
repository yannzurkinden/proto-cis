import apiClient from './client'
import type { Objective, PaginatedResponse, Action } from '@/types/api'

export interface ObjectiveFilters {
  page?: number
  size?: number
  beneficiary_id?: number
  pai_id?: number
  status?: string
  objective_type?: string
  term?: string
  overdue?: boolean
}

export const objectivesApi = {
  list: async (filters: ObjectiveFilters = {}): Promise<PaginatedResponse<Objective>> => {
    const response = await apiClient.get<PaginatedResponse<Objective>>('/objectives', {
      params: filters,
    })
    return response.data
  },

  getOverview: async (unitId?: number) => {
    const response = await apiClient.get('/objectives/overview', {
      params: { unit_id: unitId },
    })
    return response.data
  },

  get: async (id: number): Promise<Objective> => {
    const response = await apiClient.get<Objective>(`/objectives/${id}`)
    return response.data
  },

  create: async (data: Partial<Objective>): Promise<Objective> => {
    const response = await apiClient.post<Objective>('/objectives', data)
    return response.data
  },

  update: async (id: number, data: Partial<Objective>): Promise<Objective> => {
    const response = await apiClient.put<Objective>(`/objectives/${id}`, data)
    return response.data
  },

  updateProgress: async (id: number, progress: number, note?: string): Promise<Objective> => {
    const response = await apiClient.patch<Objective>(`/objectives/${id}/progress`, {
      progress,
      note,
    })
    return response.data
  },

  updateStatus: async (id: number, status: string, note?: string): Promise<Objective> => {
    const response = await apiClient.patch<Objective>(`/objectives/${id}/status`, {
      status,
      note,
    })
    return response.data
  },

  // Actions
  getActions: async (objectiveId: number): Promise<Action[]> => {
    const response = await apiClient.get<Action[]>(`/objectives/${objectiveId}/actions`)
    return response.data
  },

  createAction: async (objectiveId: number, data: Partial<Action>): Promise<Action> => {
    const response = await apiClient.post<Action>(`/objectives/${objectiveId}/actions`, data)
    return response.data
  },

  updateAction: async (objectiveId: number, actionId: number, data: Partial<Action>): Promise<Action> => {
    const response = await apiClient.put<Action>(`/objectives/${objectiveId}/actions/${actionId}`, data)
    return response.data
  },

  deleteAction: async (objectiveId: number, actionId: number): Promise<void> => {
    await apiClient.delete(`/objectives/${objectiveId}/actions/${actionId}`)
  },

  // Indicators
  achieveIndicator: async (objectiveId: number, indicatorId: number) => {
    const response = await apiClient.post(`/objectives/${objectiveId}/indicators/${indicatorId}/achieve`)
    return response.data
  },
}
