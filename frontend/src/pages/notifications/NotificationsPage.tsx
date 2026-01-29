import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  BellOff,
  CheckCheck,
  AlertTriangle,
  Clock,
  BookOpen,
  CalendarDays,
  Info,
  Circle,
} from 'lucide-react'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'

import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { notificationsApi } from '@/api/notifications'
import { useNotificationStore } from '@/stores/notificationStore'
import type { Notification } from '@/api/notifications'

const typeConfig: Record<string, { icon: React.ElementType; color: string; bgColor: string }> = {
  objective_overdue: {
    icon: AlertTriangle,
    color: 'text-red-600',
    bgColor: 'bg-red-100',
  },
  reminder: {
    icon: Clock,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
  },
  journal_new: {
    icon: BookOpen,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
  },
  absence_to_validate: {
    icon: CalendarDays,
    color: 'text-orange-600',
    bgColor: 'bg-orange-100',
  },
  system: {
    icon: Info,
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
  },
  info: {
    icon: Info,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
  },
}

function getNotificationLink(notification: Notification): string | null {
  if (!notification.link_type || !notification.link_id) return null
  switch (notification.link_type) {
    case 'objective':
      return '/objectives/' + String(notification.link_id)
    case 'beneficiary':
      return '/beneficiaries/' + String(notification.link_id)
    case 'journal':
      return '/journal/' + String(notification.link_id)
    case 'absence':
      return '/beneficiaries/' + String(notification.link_id) + '/time'
    default:
      return null
  }
}

export function NotificationsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { setUnreadCount, clearUnread } = useNotificationStore()

  const { data, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.list({ size: 50 }),
  })

  useEffect(() => {
    if (data?.unread_count !== undefined) {
      setUnreadCount(data.unread_count)
    }
  }, [data, setUnreadCount])

  const markAsReadMutation = useMutation({
    mutationFn: (id: number) => notificationsApi.markAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const markAllAsReadMutation = useMutation({
    mutationFn: () => notificationsApi.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      clearUnread()
    },
  })

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.is_read) {
      markAsReadMutation.mutate(notification.id)
    }
    const link = getNotificationLink(notification)
    if (link) {
      navigate(link)
    }
  }

  const formatDateDisplay = (dateStr: string) => {
    try {
      return format(new Date(dateStr), "dd MMM yyyy 'a' HH:mm", { locale: fr })
    } catch {
      return dateStr
    }
  }

  const unreadCount = data?.unread_count ?? 0
  const items = data?.items ?? []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Notifications</h1>
          <p className="text-muted-foreground">
            {unreadCount > 0
              ? String(unreadCount) + ' notification' + (unreadCount > 1 ? 's' : '') + ' non lue' + (unreadCount > 1 ? 's' : '')
              : 'Toutes les notifications sont lues'}
          </p>
        </div>
        {unreadCount > 0 && (
          <Button
            variant="outline"
            onClick={() => markAllAsReadMutation.mutate()}
            disabled={markAllAsReadMutation.isPending}
          >
            <CheckCheck className="mr-2 h-4 w-4" />
            Tout marquer comme lu
          </Button>
        )}
      </div>

      {/* Notifications list */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-4 p-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="flex items-start gap-4">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : !items.length ? (
            <div className="flex flex-col items-center justify-center p-12 text-center">
              <BellOff className="mb-4 h-12 w-12 text-muted-foreground" />
              <p className="text-lg font-medium">Aucune notification</p>
              <p className="text-muted-foreground">
                Vous n&apos;avez aucune notification pour le moment.
              </p>
            </div>
          ) : (
            <div className="divide-y">
              {items.map((notification: Notification) => {
                const config = typeConfig[notification.type] || typeConfig.info
                const IconComponent = config.icon
                const link = getNotificationLink(notification)

                return (
                  <div
                    key={notification.id}
                    className={
                      'flex items-start gap-4 p-4 transition-colors ' +
                      (!notification.is_read ? 'bg-accent/50 ' : '') +
                      (link ? 'cursor-pointer hover:bg-accent ' : '')
                    }
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <div className={'flex h-10 w-10 items-center justify-center rounded-full ' + config.bgColor}>
                      <IconComponent className={'h-5 w-5 ' + config.color} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className={'text-sm font-medium ' + (!notification.is_read ? 'font-semibold' : '')}>
                          {notification.title}
                        </p>
                        {!notification.is_read && (
                          <Circle className="h-2 w-2 fill-primary text-primary" />
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{notification.message}</p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {formatDateDisplay(notification.created_at)}
                      </p>
                    </div>

                    {!notification.is_read && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          markAsReadMutation.mutate(notification.id)
                        }}
                        disabled={markAsReadMutation.isPending}
                      >
                        Marquer comme lu
                      </Button>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
