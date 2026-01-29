import apiClient from './client'

export interface Notification {
  id: number
  user_id: number
  type: 'objective_overdue' | 'reminder' | 'journal_new' | 'absence_to_validate' | 'system' | 'info'
  title: string
  message: string
  is_read: boolean
  link_type: string | null
  link_id: number | null
  created_at: string
}

export interface NotificationSummary {
  unread_count: number
  notifications: Notification[]
}

export const notificationsApi = {
  list: async (params?: { is_read?: boolean; page?: number; size?: number }): Promise<{
    items: Notification[]
    total: number
    unread_count: number
  }> => {
    const response = await apiClient.get('/notifications', { params })
    return response.data
  },

  getUnreadCount: async (): Promise<{ count: number }> => {
    const response = await apiClient.get<{ count: number }>('/notifications/unread-count')
    return response.data
  },

  markAsRead: async (id: number): Promise<void> => {
    await apiClient.post(`/notifications/${id}/read`)
  },

  markAllAsRead: async (): Promise<void> => {
    await apiClient.post('/notifications/read-all')
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/notifications/${id}`)
  },
}
