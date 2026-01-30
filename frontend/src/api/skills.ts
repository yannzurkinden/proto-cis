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
    interface BackendSkillEval {
      id: number
      skill_id: number
      skill_name: string | null
      level: string
      evaluation_date: string
      evaluated_by: number
      comments: string | null
    }
    const response = await apiClient.get<BackendSkillEval[]>(
      `/skills/beneficiaries/${beneficiaryId}/skills`
    )
    return response.data.map((ev) => ({
      id: ev.id,
      beneficiary_id: beneficiaryId,
      skill_id: ev.skill_id,
      skill_name: ev.skill_name || '',
      skill_category: '',
      level: ev.level as SkillEvaluation['level'],
      evaluated_at: ev.evaluation_date,
      evaluated_by: ev.evaluated_by,
      evaluated_by_name: null,
      notes: ev.comments,
    }))
  },

  createEvaluation: async (
    beneficiaryId: number,
    data: { skill_id: number; level: string; notes?: string }
  ): Promise<SkillEvaluation> => {
    const response = await apiClient.put<{ id: number; skill_id: number; skill_name: string | null; level: string; evaluation_date: string; evaluated_by: number; comments: string | null }>(
      `/skills/beneficiaries/${beneficiaryId}/skills/${data.skill_id}`,
      { level: data.level, comments: data.notes }
    )
    const ev = response.data
    return {
      id: ev.id,
      beneficiary_id: beneficiaryId,
      skill_id: ev.skill_id,
      skill_name: ev.skill_name || '',
      skill_category: '',
      level: ev.level as SkillEvaluation['level'],
      evaluated_at: ev.evaluation_date,
      evaluated_by: ev.evaluated_by,
      evaluated_by_name: null,
      notes: ev.comments,
    }
  },

  // Trainings
  getTrainings: async (beneficiaryId: number): Promise<Training[]> => {
    const response = await apiClient.get<Training[]>(
      `/skills/beneficiaries/${beneficiaryId}/trainings`
    )
    return response.data
  },

  createTraining: async (beneficiaryId: number, data: Partial<Training>): Promise<Training> => {
    const payload = {
      title: data.title,
      training_date: data.start_date,
      end_date: data.end_date,
      duration_hours: data.duration_hours,
      trainer: data.trainer,
      location: data.location,
      certificate_obtained: data.certificate,
      notes: data.notes,
    }
    const response = await apiClient.post<Training>(
      `/skills/beneficiaries/${beneficiaryId}/trainings`,
      payload
    )
    return response.data
  },

  updateTraining: async (
    beneficiaryId: number,
    trainingId: number,
    data: Partial<Training>
  ): Promise<Training> => {
    const response = await apiClient.put<Training>(
      `/skills/beneficiaries/${beneficiaryId}/trainings/${trainingId}`,
      data
    )
    return response.data
  },

  deleteTraining: async (beneficiaryId: number, trainingId: number): Promise<void> => {
    await apiClient.delete(`/skills/beneficiaries/${beneficiaryId}/trainings/${trainingId}`)
  },
}
