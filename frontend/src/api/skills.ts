import apiClient from './client'

export interface Skill {
  id: number
  name: string
  category: string
  description: string | null
  is_active: boolean
  created_at: string
}

export interface SkillEvaluation {
  id: number
  beneficiary_id: number
  skill_id: number
  skill_name: string
  skill_category: string
  level: 'not_acquired' | 'in_progress' | 'acquired' | 'mastered'
  evaluated_at: string
  evaluated_by: number
  evaluated_by_name: string | null
  notes: string | null
}

export interface Training {
  id: number
  beneficiary_id: number
  title: string
  description: string | null
  start_date: string
  end_date: string | null
  duration_hours: number | null
  trainer: string | null
  location: string | null
  certificate: boolean
  certificate_url: string | null
  notes: string | null
  created_at: string
}

export const skillsApi = {
  // Skill reference
  listSkills: async (): Promise<Skill[]> => {
    const response = await apiClient.get<Skill[]>('/skills')
    return response.data
  },

  createSkill: async (data: Partial<Skill>): Promise<Skill> => {
    const response = await apiClient.post<Skill>('/skills', data)
    return response.data
  },

  updateSkill: async (id: number, data: Partial<Skill>): Promise<Skill> => {
    const response = await apiClient.put<Skill>(`/skills/${id}`, data)
    return response.data
  },

  deleteSkill: async (id: number): Promise<void> => {
    await apiClient.delete(`/skills/${id}`)
  },

  // Skill evaluations
  getEvaluations: async (beneficiaryId: number): Promise<SkillEvaluation[]> => {
    const response = await apiClient.get<SkillEvaluation[]>(
      `/beneficiaries/${beneficiaryId}/skills/evaluations`
    )
    return response.data
  },

  createEvaluation: async (
    beneficiaryId: number,
    data: { skill_id: number; level: string; notes?: string }
  ): Promise<SkillEvaluation> => {
    const response = await apiClient.post<SkillEvaluation>(
      `/beneficiaries/${beneficiaryId}/skills/evaluations`,
      data
    )
    return response.data
  },

  // Trainings
  getTrainings: async (beneficiaryId: number): Promise<Training[]> => {
    const response = await apiClient.get<Training[]>(
      `/beneficiaries/${beneficiaryId}/trainings`
    )
    return response.data
  },

  createTraining: async (beneficiaryId: number, data: Partial<Training>): Promise<Training> => {
    const response = await apiClient.post<Training>(
      `/beneficiaries/${beneficiaryId}/trainings`,
      data
    )
    return response.data
  },

  updateTraining: async (
    beneficiaryId: number,
    trainingId: number,
    data: Partial<Training>
  ): Promise<Training> => {
    const response = await apiClient.put<Training>(
      `/beneficiaries/${beneficiaryId}/trainings/${trainingId}`,
      data
    )
    return response.data
  },

  deleteTraining: async (beneficiaryId: number, trainingId: number): Promise<void> => {
    await apiClient.delete(`/beneficiaries/${beneficiaryId}/trainings/${trainingId}`)
  },
}
