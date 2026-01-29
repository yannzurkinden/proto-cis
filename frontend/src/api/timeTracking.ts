import apiClient from './client'

export interface TimeEntry {
  id: number
  beneficiary_id: number
  date: string
  time_in: string
  time_out: string | null
  entry_type: 'present' | 'half_day' | 'training' | 'external'
  hours: number | null
  notes: string | null
  created_at: string
  created_by: number | null
}

export interface Absence {
  id: number
  beneficiary_id: number
  start_date: string
  end_date: string
  absence_type: 'sick' | 'vacation' | 'personal' | 'accident' | 'unjustified' | 'other'
  duration_days: number
  reason: string | null
  justified: boolean
  validated: boolean
  validated_by: number | null
  validated_by_name: string | null
  validated_at: string | null
  notes: string | null
  created_at: string
}

export interface VacationBalance {
  year: number
  entitled_days: number
  taken_days: number
  remaining_days: number
  planned_days: number
}

export interface TimeStats {
  absence_rate: number
  hours_this_month: number
  absences_this_month: number
}

export interface MonthlySummary {
  month: string
  total_hours: number
  working_days: number
  present_days: number
  absent_days: number
}

export const timeTrackingApi = {
  // Time entries
  getEntries: async (
    beneficiaryId: number,
    params?: { month?: string; year?: number }
  ): Promise<TimeEntry[]> => {
    const response = await apiClient.get<TimeEntry[]>(
      `/beneficiaries/${beneficiaryId}/time-entries`,
      { params }
    )
    return response.data
  },

  createEntry: async (beneficiaryId: number, data: Partial<TimeEntry>): Promise<TimeEntry> => {
    const response = await apiClient.post<TimeEntry>(
      `/beneficiaries/${beneficiaryId}/time-entries`,
      data
    )
    return response.data
  },

  updateEntry: async (
    beneficiaryId: number,
    entryId: number,
    data: Partial<TimeEntry>
  ): Promise<TimeEntry> => {
    const response = await apiClient.put<TimeEntry>(
      `/beneficiaries/${beneficiaryId}/time-entries/${entryId}`,
      data
    )
    return response.data
  },

  deleteEntry: async (beneficiaryId: number, entryId: number): Promise<void> => {
    await apiClient.delete(`/beneficiaries/${beneficiaryId}/time-entries/${entryId}`)
  },

  // Absences
  getAbsences: async (
    beneficiaryId: number,
    params?: { year?: number }
  ): Promise<Absence[]> => {
    const response = await apiClient.get<Absence[]>(
      `/beneficiaries/${beneficiaryId}/absences`,
      { params }
    )
    return response.data
  },

  createAbsence: async (beneficiaryId: number, data: Partial<Absence>): Promise<Absence> => {
    const response = await apiClient.post<Absence>(
      `/beneficiaries/${beneficiaryId}/absences`,
      data
    )
    return response.data
  },

  validateAbsence: async (beneficiaryId: number, absenceId: number): Promise<Absence> => {
    const response = await apiClient.post<Absence>(
      `/beneficiaries/${beneficiaryId}/absences/${absenceId}/validate`
    )
    return response.data
  },

  deleteAbsence: async (beneficiaryId: number, absenceId: number): Promise<void> => {
    await apiClient.delete(`/beneficiaries/${beneficiaryId}/absences/${absenceId}`)
  },

  // Vacation balance
  getVacationBalance: async (beneficiaryId: number, year?: number): Promise<VacationBalance> => {
    const response = await apiClient.get<VacationBalance>(
      `/beneficiaries/${beneficiaryId}/vacation-balance`,
      { params: { year } }
    )
    return response.data
  },

  // Stats
  getStats: async (beneficiaryId: number): Promise<TimeStats> => {
    const response = await apiClient.get<TimeStats>(
      `/beneficiaries/${beneficiaryId}/absence-stats`
    )
    return response.data
  },

  // Monthly summary
  getMonthlySummary: async (
    beneficiaryId: number,
    year: number,
    month: number
  ): Promise<MonthlySummary> => {
    const response = await apiClient.get<MonthlySummary>(
      `/beneficiaries/${beneficiaryId}/time-entries/monthly-summary`,
      { params: { year, month } }
    )
    return response.data
  },
}
