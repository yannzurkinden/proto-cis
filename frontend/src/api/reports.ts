import apiClient from './client'

export const reportsApi = {
  generateBeneficiarySummary: async (beneficiaryId: number): Promise<Blob> => {
    const response = await apiClient.get(
      `/reports/beneficiary/${beneficiaryId}/summary`,
      { responseType: 'blob' }
    )
    return response.data
  },

  generateActivityReport: async (params: {
    date_from: string
    date_to: string
    unit_id?: number
  }): Promise<Blob> => {
    const response = await apiClient.get('/reports/activity', {
      params,
      responseType: 'blob',
    })
    return response.data
  },

  generateObjectivesReport: async (params: {
    status?: string
    objective_type?: string
    unit_id?: number
  }): Promise<Blob> => {
    const response = await apiClient.get('/reports/objectives', {
      params,
      responseType: 'blob',
    })
    return response.data
  },

  generateAbsenceStats: async (params: {
    unit_id?: number
    date_from: string
    date_to: string
  }): Promise<Blob> => {
    const response = await apiClient.get('/reports/absenteeism', {
      params,
      responseType: 'blob',
    })
    return response.data
  },
}
