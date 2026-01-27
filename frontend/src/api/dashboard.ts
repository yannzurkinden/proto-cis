import apiClient from './client'

export interface MSPDashboard {
  my_beneficiaries: Array<{
    id: number
    name: string
    photo_url: string | null
    status: string
    objectives_overdue: number
    last_journal_entry: string | null
  }>
  today_reminders: Array<{
    type: string
    beneficiary_id: number
    beneficiary_name: string
    objective_id?: number
    objective_title?: string
    due_date?: string
    message?: string
  }>
  recent_journal_entries: Array<{
    id: number
    beneficiary_name: string
    title: string
    entry_date: string
  }>
  pending_tasks: Array<Record<string, unknown>>
}

export interface ManagementDashboard {
  summary: {
    total_beneficiaries: number
    active_beneficiaries: number
    new_this_month: number
    exited_this_month: number
  }
  objectives_overview: {
    total: number
    achieved_this_month: number
    overdue: number
    achievement_rate: number
  }
  absence_stats: {
    global_rate: number
    by_unit: Array<{
      unit_id: number
      unit_name: string
      rate: number
    }>
  }
  alerts: Array<{
    type: string
    beneficiary_id: number
    beneficiary_name: string
    message: string
  }>
}

export const dashboardApi = {
  getMSPDashboard: async (): Promise<MSPDashboard> => {
    const response = await apiClient.get<MSPDashboard>('/dashboard/msp')
    return response.data
  },

  getManagementDashboard: async (unitId?: number): Promise<ManagementDashboard> => {
    const response = await apiClient.get<ManagementDashboard>('/dashboard/management', {
      params: { unit_id: unitId },
    })
    return response.data
  },
}
