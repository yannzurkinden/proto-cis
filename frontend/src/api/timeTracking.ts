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

interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

interface BackendTimeEntry {
  id: number
  beneficiary_id: number
  entry_date: string
  time_in: string | null
  time_out: string | null
  entry_type: string
  hours_worked: number | null
  notes: string | null
}

interface BackendAbsence {
  id: number
  beneficiary_id: number
  absence_type: string
  start_date: string
  end_date: string
  notes: string | null
  justification_document_id: number | null
  validated_by: number | null
  validated_at: string | null
  duration_days: number
}

function mapTimeEntry(e: BackendTimeEntry): TimeEntry {
  return {
    id: e.id,
    beneficiary_id: e.beneficiary_id,
    date: e.entry_date,
    time_in: e.time_in ?? '',
    time_out: e.time_out,
    entry_type: e.entry_type as TimeEntry['entry_type'],
    hours: e.hours_worked != null ? Number(e.hours_worked) : null,
    notes: e.notes,
    created_at: '',
    created_by: null,
  }
}

function mapAbsence(a: BackendAbsence): Absence {
  return {
    id: a.id,
    beneficiary_id: a.beneficiary_id,
    start_date: a.start_date,
    end_date: a.end_date,
    absence_type: a.absence_type as Absence['absence_type'],
    duration_days: a.duration_days,
    reason: a.notes,
    justified: a.justification_document_id != null,
    validated: a.validated_by != null,
    validated_by: a.validated_by,
    validated_by_name: null,
    validated_at: a.validated_at,
    notes: a.notes,
    created_at: '',
  }
}

export const timeTrackingApi = {
  // Time entries
  getEntries: async (
    beneficiaryId: number,
    params?: { month?: string; year?: number }
  ): Promise<TimeEntry[]> => {
    const response = await apiClient.get<PaginatedResponse<BackendTimeEntry>>(
      `/beneficiaries/${beneficiaryId}/time-entries`,
      { params }
    )
    return (response.data.items || []).map(mapTimeEntry)
  },

  createEntry: async (beneficiaryId: number, data: Partial<TimeEntry>): Promise<TimeEntry> => {
    const payload = {
      entry_date: data.date,
      time_in: data.time_in || undefined,
      time_out: data.time_out || undefined,
      entry_type: data.entry_type || 'work',
      notes: data.notes || undefined,
    }
    const response = await apiClient.post<BackendTimeEntry>(
      `/beneficiaries/${beneficiaryId}/time-entries`,
      payload
    )
    return mapTimeEntry(response.data)
  },

  updateEntry: async (
    beneficiaryId: number,
    entryId: number,
    data: Partial<TimeEntry>
  ): Promise<TimeEntry> => {
    const payload = {
      time_in: data.time_in || undefined,
      time_out: data.time_out || undefined,
      entry_type: data.entry_type || undefined,
      notes: data.notes || undefined,
    }
    const response = await apiClient.put<BackendTimeEntry>(
      `/beneficiaries/${beneficiaryId}/time-entries/${entryId}`,
      payload
    )
    return mapTimeEntry(response.data)
  },

  deleteEntry: async (beneficiaryId: number, entryId: number): Promise<void> => {
    await apiClient.delete(`/beneficiaries/${beneficiaryId}/time-entries/${entryId}`)
  },

  // Absences
  getAbsences: async (
    beneficiaryId: number,
    params?: { year?: number }
  ): Promise<Absence[]> => {
    const response = await apiClient.get<PaginatedResponse<BackendAbsence>>(
      `/beneficiaries/${beneficiaryId}/absences`,
      { params }
    )
    return (response.data.items || []).map(mapAbsence)
  },

  createAbsence: async (beneficiaryId: number, data: Partial<Absence>): Promise<Absence> => {
    const payload = {
      absence_type: data.absence_type,
      start_date: data.start_date,
      end_date: data.end_date,
      notes: data.reason || data.notes || undefined,
    }
    const response = await apiClient.post<BackendAbsence>(
      `/beneficiaries/${beneficiaryId}/absences`,
      payload
    )
    return mapAbsence(response.data)
  },

  validateAbsence: async (beneficiaryId: number, absenceId: number): Promise<Absence> => {
    const response = await apiClient.post<BackendAbsence>(
      `/beneficiaries/${beneficiaryId}/absences/${absenceId}/validate`
    )
    return mapAbsence(response.data)
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
    const response = await apiClient.get<{ total_days: number; by_type: Record<string, number>; absence_rate: number }>(
      `/beneficiaries/${beneficiaryId}/absence-stats`
    )
    const data = response.data
    return {
      absence_rate: data.absence_rate ?? 0,
      hours_this_month: 0,
      absences_this_month: data.total_days ?? 0,
    }
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
